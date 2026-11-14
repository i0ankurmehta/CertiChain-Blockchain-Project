import csv
import hashlib
import ipaddress
import io
import json
import math
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

import streamlit as st


st.set_page_config(page_title="CertiChain", page_icon="🎓", layout="wide")

DIFFICULTY = 3
MAX_IMPORT_BYTES = 2 * 1024 * 1024  # 2 MB
MAX_RECORDS = 500
SYNTHETIC_DATA_PATH = Path(__file__).parent / "data" / "synthetic_records.json"
REQUIRED_FIELDS = {"student_name", "roll_no", "course", "cgpa"}
DATA_SOURCE_OPTIONS = [
    "Manual entry",
    "Synthetic demo",
    "Upload CSV / JSON",
    "Online JSON",
]


class CertificateBlock:
    def __init__(self, index, student_name, roll_no, course, cgpa, previous_hash):
        self.index = index
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.certificate_data = {
            "student_name": student_name,
            "roll_no": roll_no,
            "course": course,
            "cgpa": float(cgpa),
        }
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_content = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "certificate_data": self.certificate_data,
                "previous_hash": self.previous_hash,
                "nonce": self.nonce,
            },
            sort_keys=True,
        )
        return hashlib.sha256(block_content.encode("utf-8")).hexdigest()

    def mine_block(self, difficulty=DIFFICULTY):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()


def create_genesis_block():
    """Create the starting block for an independent ledger."""
    block = CertificateBlock(
        0, "GENESIS_BLOCK", "0000", "System Init", 0.0, "0" * 64
    )
    block.mine_block(DIFFICULTY)
    return block


def validate_records(records):
    """Validate and normalise records before adding them to a local demo chain."""
    if not isinstance(records, list) or not records:
        raise ValueError("The source must contain a non-empty list of records.")
    if len(records) > MAX_RECORDS:
        raise ValueError(f"A maximum of {MAX_RECORDS} records can be imported at once.")

    clean_records = []
    for number, record in enumerate(records, start=1):
        if not isinstance(record, dict) or not REQUIRED_FIELDS.issubset(record):
            missing = REQUIRED_FIELDS - set(record) if isinstance(record, dict) else REQUIRED_FIELDS
            raise ValueError(
                f"Record #{number} is missing required fields: {', '.join(sorted(missing))}."
            )

        student_name = "" if record["student_name"] is None else str(record["student_name"]).strip()
        roll_no = "" if record["roll_no"] is None else str(record["roll_no"]).strip()
        course = "" if record["course"] is None else str(record["course"]).strip()
        try:
            cgpa = float(record["cgpa"])
        except (TypeError, ValueError) as error:
            raise ValueError(f"Record #{number} has a non-numeric CGPA.") from error

        if not student_name or not roll_no or not course:
            raise ValueError(f"Record #{number} has an empty name, roll number or course.")
        if not math.isfinite(cgpa) or not 0.0 <= cgpa <= 10.0:
            raise ValueError(f"Record #{number} has an invalid CGPA; use a value from 0 to 10.")

        clean_records.append(
            {
                "student_name": student_name,
                "roll_no": roll_no,
                "course": course,
                "cgpa": cgpa,
            }
        )

    return clean_records


def create_chain_from_records(records):
    """Create and mine a fresh chain from validated records."""
    clean_records = validate_records(records)
    chain = [create_genesis_block()]
    for record in clean_records:
        previous = chain[-1]
        block = CertificateBlock(
            index=len(chain),
            student_name=record["student_name"],
            roll_no=record["roll_no"],
            course=record["course"],
            cgpa=record["cgpa"],
            previous_hash=previous.hash,
        )
        block.mine_block(DIFFICULTY)
        chain.append(block)
    return chain


def records_from_json(payload):
    """Accept either {"records": [...]}, a single record, or a list of records."""
    if isinstance(payload, dict) and "records" in payload:
        records = payload["records"]
        dataset_name = str(payload.get("dataset_name", "Imported JSON records"))
    elif isinstance(payload, dict):
        records = [payload]
        dataset_name = "Imported JSON record"
    elif isinstance(payload, list):
        records = payload
        dataset_name = "Imported JSON records"
    else:
        raise ValueError("JSON must be a record, a list of records, or an object with a 'records' list.")

    return validate_records(records), dataset_name


def records_from_csv(file_bytes):
    """Read a CSV whose headers match the required CertiChain record fields."""
    try:
        csv_text = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("CSV must be encoded as UTF-8.") from error

    reader = csv.DictReader(io.StringIO(csv_text))
    if not reader.fieldnames:
        raise ValueError("The CSV is empty or has no header row.")

    missing = REQUIRED_FIELDS - set(reader.fieldnames)
    if missing:
        raise ValueError(f"CSV is missing these column headers: {', '.join(sorted(missing))}.")

    return validate_records(list(reader)), "Imported CSV records"


def load_synthetic_dataset():
    """Read the fictional demo dataset stored in the repository."""
    with SYNTHETIC_DATA_PATH.open("r", encoding="utf-8") as dataset_file:
        dataset = json.load(dataset_file)

    if not isinstance(dataset, dict):
        raise ValueError("The repository synthetic dataset must be a JSON object.")

    records = validate_records(dataset.get("records"))
    return {
        "dataset_name": dataset.get("dataset_name", "Synthetic demonstration records"),
        "records": records,
    }


def get_allowed_source_hosts():
    """Read exact host allow-list entries from local Streamlit secrets."""
    try:
        config = st.secrets.get("certichain", {})
        configured_hosts = config.get("allowed_source_hosts", [])
    except Exception:
        configured_hosts = []

    if not isinstance(configured_hosts, (list, tuple)):
        return set()
    return {str(host).strip().lower().rstrip(".") for host in configured_hosts if str(host).strip()}


class BlockRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Do not follow redirects; each final issuer host must be allow-listed explicitly."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_approved_json_endpoint(url):
    """Fetch bounded JSON from an explicitly allow-listed HTTPS host."""
    parsed = urllib.parse.urlsplit(url.strip())
    if parsed.scheme.lower() != "https":
        raise ValueError("Only HTTPS source URLs are permitted.")
    if not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Enter a valid HTTPS URL without embedded username or password.")
    if parsed.port not in (None, 443):
        raise ValueError("Only the standard HTTPS port (443) is permitted.")
    if parsed.fragment:
        raise ValueError("URL fragments are not supported.")

    hostname = parsed.hostname.lower().rstrip(".")
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        raise ValueError("Use an approved DNS hostname, not an IP address.")

    allowed_hosts = get_allowed_source_hosts()
    if not allowed_hosts:
        raise ValueError("No approved source hosts are configured in .streamlit/secrets.toml.")
    if hostname not in allowed_hosts:
        raise ValueError(f"'{hostname}' is not in the configured source-host allow-list.")

    request = urllib.request.Request(
        url.strip(),
        headers={
            "Accept": "application/json",
            "User-Agent": "CertiChain-Research-Prototype/1.0",
        },
        method="GET",
    )
    context = ssl.create_default_context()
    opener = urllib.request.build_opener(
        BlockRedirectHandler,
        urllib.request.HTTPSHandler(context=context),
    )

    try:
        with opener.open(request, timeout=10) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            if "json" not in content_type:
                raise ValueError("The approved endpoint must return an application/json response.")
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > MAX_IMPORT_BYTES:
                raise ValueError("The online response exceeds the 2 MB import limit.")
            raw_data = response.read(MAX_IMPORT_BYTES + 1)
    except urllib.error.HTTPError as error:
        if error.code in (301, 302, 303, 307, 308):
            raise ValueError("Redirect blocked. Use the final HTTPS endpoint and allow-list its host.") from error
        raise ValueError(f"Online source returned HTTP {error.code}.") from error
    except urllib.error.URLError as error:
        raise ValueError(f"Could not reach the approved online source: {error.reason}") from error

    if len(raw_data) > MAX_IMPORT_BYTES:
        raise ValueError("The online response exceeds the 2 MB import limit.")

    try:
        payload = json.loads(raw_data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("The online endpoint did not return valid UTF-8 JSON.") from error

    return records_from_json(payload)


def audit_chain(chain):
    """Verify the genesis block, each block hash, proof of work, and chain links."""
    if not chain:
        return False, set()

    broken_blocks = set()
    is_valid = True

    genesis = chain[0]
    genesis_invalid = (
        genesis.index != 0
        or genesis.previous_hash != "0" * 64
        or genesis.hash != genesis.calculate_hash()
        or not genesis.hash.startswith("0" * DIFFICULTY)
    )
    if genesis_invalid:
        broken_blocks.add(0)
        is_valid = False

    for index in range(1, len(chain)):
        current = chain[index]
        previous = chain[index - 1]

        content_changed = current.hash != current.calculate_hash()
        proof_of_work_invalid = not current.hash.startswith("0" * DIFFICULTY)
        link_broken = current.previous_hash != previous.hash
        predecessor_compromised = (index - 1) in broken_blocks

        if content_changed or proof_of_work_invalid or link_broken or predecessor_compromised:
            is_valid = False
            broken_blocks.add(index)

    return is_valid, broken_blocks


def initialise_session_state():
    defaults = {
        "manual_chain": None,
        "synthetic_chain": None,
        "synthetic_dataset_name": "Synthetic demonstration records",
        "imported_chain": None,
        "imported_records": None,
        "imported_dataset_name": None,
        "imported_source_digest": None,
        "imported_source_mode": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if st.session_state.manual_chain is None:
        st.session_state.manual_chain = [create_genesis_block()]


initialise_session_state()

st.title("CertiChain")
st.caption("Academic credential ledger")

with st.sidebar:
    data_source = st.selectbox("Data source", DATA_SOURCE_OPTIONS)

    if data_source == "Synthetic demo":
        if st.session_state.synthetic_chain is None:
            try:
                dataset = load_synthetic_dataset()
                st.session_state.synthetic_chain = create_chain_from_records(dataset["records"])
                st.session_state.synthetic_dataset_name = dataset["dataset_name"]
            except (OSError, json.JSONDecodeError, ValueError, TypeError) as error:
                st.error(f"Could not load synthetic records: {error}")
                st.stop()

        st.caption(f"{st.session_state.synthetic_dataset_name} · fictional")

    elif data_source == "Upload CSV / JSON":
        st.caption("CSV or JSON · max 2 MB")
        uploaded_file = st.file_uploader(
            "Select file",
            type=["csv", "json"],
            key="external_data_upload",
        )
        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            if len(file_bytes) > MAX_IMPORT_BYTES:
                st.error("The selected file exceeds the 2 MB import limit.")
            else:
                digest = hashlib.sha256(file_bytes).hexdigest()
                if (
                    digest != st.session_state.imported_source_digest
                    or st.session_state.imported_source_mode != data_source
                ):
                    try:
                        if uploaded_file.name.lower().endswith(".csv"):
                            records, dataset_name = records_from_csv(file_bytes)
                        else:
                            payload = json.loads(file_bytes.decode("utf-8-sig"))
                            records, dataset_name = records_from_json(payload)

                        st.session_state.imported_records = records
                        st.session_state.imported_chain = create_chain_from_records(records)
                        st.session_state.imported_dataset_name = f"{dataset_name} — {uploaded_file.name}"
                        st.session_state.imported_source_digest = digest
                        st.session_state.imported_source_mode = data_source
                        st.success(f"Imported {len(records)} records.")
                    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError) as error:
                        st.session_state.imported_records = None
                        st.session_state.imported_chain = None
                        st.session_state.imported_dataset_name = None
                        st.session_state.imported_source_digest = digest
                        st.session_state.imported_source_mode = data_source
                        st.error(f"Could not import file: {error}")

        if (
            st.session_state.imported_source_mode == data_source
            and st.session_state.imported_chain is not None
        ):

    elif data_source == "Online JSON":
        allowed_hosts = get_allowed_source_hosts()
        if not allowed_hosts:
            st.warning("No approved hosts configured.")
            with st.expander("Configure approved hosts"):
                st.code(
                    '[certichain]\nallowed_source_hosts = ["issuer.example.edu"]',
                    language="toml",
                )
                st.caption("Save in .streamlit/secrets.toml. Keep this file private.")
        else:
            st.caption("Approved: " + ", ".join(sorted(allowed_hosts)))

        with st.form("online_source_form"):
            source_url = st.text_input(
                "HTTPS JSON URL",
                placeholder="https://issuer.example.edu/records.json",
            )
            fetch_submitted = st.form_submit_button("Fetch")

        if fetch_submitted:
            try:
                records, dataset_name = fetch_approved_json_endpoint(source_url)
                source_digest = hashlib.sha256(
                    json.dumps(records, sort_keys=True).encode("utf-8")
                ).hexdigest()
                st.session_state.imported_records = records
                st.session_state.imported_chain = create_chain_from_records(records)
                st.session_state.imported_dataset_name = f"{dataset_name} — {urllib.parse.urlsplit(source_url).hostname}"
                st.session_state.imported_source_digest = source_digest
                st.session_state.imported_source_mode = data_source
                st.success(f"Fetched {len(records)} records.")
            except (ValueError, TypeError) as error:
                st.error(f"Online import stopped: {error}")

        if st.session_state.imported_source_mode == data_source and st.session_state.imported_chain is not None:

    st.divider()

    # Select the ledger without merging or overwriting the other sources.
    if data_source == "Synthetic demo":
        active_chain = st.session_state.synthetic_chain
        ledger_label = "Synthetic demo"
    elif data_source in ("Upload CSV / JSON", "Online JSON"):
        if st.session_state.imported_source_mode == data_source:
            active_chain = st.session_state.imported_chain
        else:
            active_chain = None
        ledger_label = "Imported data"
    else:
        active_chain = st.session_state.manual_chain
        ledger_label = "Manual"

    if data_source == "Manual entry":
        st.header("Add record")
        with st.form("issue_form", clear_on_submit=True):
            name = st.text_input("Student name", placeholder="e.g., Rohan Sharma")
            roll = st.text_input("Roll number", placeholder="e.g., BCA2401")
            course = st.text_input("Course / qualification", placeholder="e.g., BCA Cybersecurity")
            cgpa = st.number_input(
                "CGPA", min_value=0.0, max_value=10.0, value=8.5, step=0.1
            )
            submitted = st.form_submit_button("Add record")

        if submitted:
            if not name.strip() or not roll.strip() or not course.strip():
                st.error("Enter the student name, roll number and course.")
            else:
                previous = st.session_state.manual_chain[-1]
                new_block = CertificateBlock(
                    index=len(st.session_state.manual_chain),
                    student_name=name.strip(),
                    roll_no=roll.strip(),
                    course=course.strip(),
                    cgpa=cgpa,
                    previous_hash=previous.hash,
                )
                new_block.mine_block(DIFFICULTY)
                st.session_state.manual_chain.append(new_block)
                st.success(f"Block #{new_block.index} added to the manual ledger.")
                st.rerun()

    elif data_source in ("Upload CSV / JSON", "Online JSON"):
        if active_chain is not None:
            if st.button("Clear imported data", use_container_width=True):
                st.session_state.imported_chain = None
                st.session_state.imported_records = None
                st.session_state.imported_dataset_name = None
                st.session_state.imported_source_digest = None
                st.session_state.imported_source_mode = None
                st.rerun()

    with st.expander("Ledger tools"):
        if active_chain is not None and len(active_chain) > 1:
            block_idx = st.number_input(
                "Block",
                min_value=1,
                max_value=len(active_chain) - 1,
                step=1,
                key=f"target_block_{data_source}",
            )
            fake_cgpa = st.number_input(
                "Test CGPA",
                min_value=0.0,
                max_value=10.0,
                value=9.9,
                step=0.1,
                key=f"fake_cgpa_{data_source}",
            )
            if st.button("Simulate tampering", use_container_width=True):
                active_chain[block_idx].certificate_data["cgpa"] = float(fake_cgpa)
                st.rerun()

        if data_source == "Manual entry":
            if st.button("Reset ledger", use_container_width=True):
                st.session_state.manual_chain = [create_genesis_block()]
                st.rerun()
        elif data_source == "Synthetic demo":
            if st.button("Reset demo", use_container_width=True):
                dataset = load_synthetic_dataset()
                st.session_state.synthetic_chain = create_chain_from_records(dataset["records"])
                st.rerun()
        elif active_chain is not None:
            if st.button("Rebuild ledger", use_container_width=True):
                st.session_state.imported_chain = create_chain_from_records(
                    st.session_state.imported_records
                )
                st.rerun()


st.subheader("Ledger")
if active_chain is None:
    st.info("No records loaded.")
    st.stop()

is_valid, broken_blocks = audit_chain(active_chain)
metric_cols = st.columns(2)
metric_cols[0].metric("Blocks", len(active_chain))
metric_cols[1].metric("Integrity", "Valid" if is_valid else "Tampered")
if not is_valid:
    st.error("Integrity check failed.")

if data_source == "Synthetic demo":
    st.caption("Fictional demo data")
elif data_source in ("Upload CSV / JSON", "Online JSON"):
    st.caption("External data · not issuer-verified")

st.dataframe(
    [
        {
            "Block": block.index,
            "Student": block.certificate_data["student_name"],
            "Roll number": block.certificate_data["roll_no"],
            "Course": block.certificate_data["course"],
            "CGPA": block.certificate_data["cgpa"],
            "Status": "Tampered" if block.index in broken_blocks else "Valid",
        }
        for block in active_chain
    ],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Block details")
for block in active_chain:
    tampered = block.index in broken_blocks
    with st.expander(f"Block #{block.index} · {'Tampered' if tampered else 'Valid'}"):
        st.caption(f"Timestamp: {block.timestamp} · Nonce: {block.nonce}")
        st.code(
            f"Previous hash: {block.previous_hash}\n"
            f"Stored hash: {block.hash}\n"
            f"Calculated hash: {block.calculate_hash()}",
            language="text",
        )
