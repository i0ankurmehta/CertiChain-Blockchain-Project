import hashlib
import json
from datetime import datetime
from pathlib import Path

import streamlit as st


st.set_page_config(page_title="CertiChain - University Ledger", layout="wide")

DIFFICULTY = 3
SYNTHETIC_DATA_PATH = Path(__file__).parent / "data" / "synthetic_records.json"


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
        return hashlib.sha256(block_content.encode()).hexdigest()

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


def create_chain_from_records(records):
    """Create and mine a fresh chain from the committed synthetic records."""
    chain = [create_genesis_block()]
    for record in records:
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


def load_synthetic_dataset():
    """Read the fictional demo dataset stored in the repository."""
    with SYNTHETIC_DATA_PATH.open("r", encoding="utf-8") as dataset_file:
        dataset = json.load(dataset_file)

    records = dataset.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("The synthetic dataset must contain a non-empty records list.")

    required_fields = {"student_name", "roll_no", "course", "cgpa"}
    for number, record in enumerate(records, start=1):
        if not isinstance(record, dict) or not required_fields.issubset(record):
            raise ValueError(f"Synthetic record #{number} is missing required fields.")
        cgpa = float(record["cgpa"])
        if not 0.0 <= cgpa <= 10.0:
            raise ValueError(f"Synthetic record #{number} has an invalid CGPA.")

    return dataset


def audit_chain(chain):
    """Verify the genesis block, each block hash, proof of work, and chain links."""
    if not chain:
        return False, set()

    broken_blocks = set()
    is_valid = True

    # Validate the genesis block as the trust anchor of this local chain.
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

        if (
            content_changed
            or proof_of_work_invalid
            or link_broken
            or predecessor_compromised
        ):
            is_valid = False
            broken_blocks.add(index)

    return is_valid, broken_blocks


def initialise_session_state():
    if "manual_chain" not in st.session_state:
        st.session_state.manual_chain = [create_genesis_block()]

    if "synthetic_chain" not in st.session_state:
        st.session_state.synthetic_chain = None

    if "synthetic_dataset_name" not in st.session_state:
        st.session_state.synthetic_dataset_name = "Synthetic demonstration records"

    if "synthetic_mode" not in st.session_state:
        st.session_state.synthetic_mode = False


initialise_session_state()

st.title("🎓 CertiChain: Tamper-Evident Academic Certificate Ledger")
st.caption("SHA-256 & Proof-of-Work Blockchain Demonstration for College Viva")

with st.sidebar:
    st.header("Demo configuration")
    synthetic_mode = st.toggle(
        "Turn on Synthetic Data Records",
        key="synthetic_mode",
        help=(
            "Loads fictional sample records from the repository into a separate "
            "demonstration ledger. Your manual ledger is preserved."
        ),
    )

    if synthetic_mode:
        if st.session_state.synthetic_chain is None:
            try:
                dataset = load_synthetic_dataset()
                st.session_state.synthetic_chain = create_chain_from_records(
                    dataset["records"]
                )
                st.session_state.synthetic_dataset_name = dataset.get(
                    "dataset_name", "Synthetic demonstration records"
                )
            except (OSError, json.JSONDecodeError, ValueError, TypeError) as error:
                st.error(f"Could not load synthetic records: {error}")
                st.stop()

        st.success("Synthetic ledger loaded")
        st.caption(st.session_state.synthetic_dataset_name)
        st.caption("Fictional demonstration data — not university records.")

    st.divider()

    # Keep the manual and synthetic ledgers separate.
    if synthetic_mode:
        active_chain = st.session_state.synthetic_chain
        st.header("1. Synthetic Ledger Controls")
        st.info(
            "Synthetic mode is ON. Manual entry is paused, but your manual ledger "
            "remains saved in this session."
        )

        if st.button("↻ Rebuild Synthetic Ledger", use_container_width=True):
            dataset = load_synthetic_dataset()
            st.session_state.synthetic_chain = create_chain_from_records(
                dataset["records"]
            )
            st.rerun()

    else:
        active_chain = st.session_state.manual_chain
        st.header("1. Issue New Certificate")

        with st.form("issue_form", clear_on_submit=True):
            name = st.text_input("Student Name", placeholder="e.g., Rohan Sharma")
            roll = st.text_input("Roll Number", placeholder="e.g., BCA2401")
            course = st.selectbox(
                "Course",
                [
                    "BCA Cybersecurity",
                    "BCA Data Science",
                    "BCA Cloud Tech",
                    "MCA",
                ],
            )
            cgpa = st.number_input(
                "CGPA",
                min_value=0.0,
                max_value=10.0,
                value=8.5,
                step=0.1,
            )
            submitted = st.form_submit_button("⛏️ Mine & Issue Certificate")

        if submitted:
            if not name.strip() or not roll.strip():
                st.error("Enter both Student Name and Roll Number.")
            else:
                previous = st.session_state.manual_chain[-1]
                new_block = CertificateBlock(
                    index=len(st.session_state.manual_chain),
                    student_name=name.strip(),
                    roll_no=roll.strip(),
                    course=course,
                    cgpa=cgpa,
                    previous_hash=previous.hash,
                )
                new_block.mine_block(DIFFICULTY)
                st.session_state.manual_chain.append(new_block)
                st.success(f"Block #{new_block.index} mined!")
                st.rerun()

    st.divider()
    st.header("2. 🚨 Simulate Hacker Attack")

    if len(active_chain) > 1:
        block_idx = st.number_input(
            "Target Block #",
            min_value=1,
            max_value=len(active_chain) - 1,
            step=1,
            key="synthetic_target_block" if synthetic_mode else "manual_target_block",
        )
        fake_cgpa = st.number_input(
            "Inject Fake CGPA",
            min_value=0.0,
            max_value=10.0,
            value=9.9,
            step=0.1,
            key="synthetic_fake_cgpa" if synthetic_mode else "manual_fake_cgpa",
        )

        if st.button("Tamper Database Record"):
            active_chain[block_idx].certificate_data["cgpa"] = float(fake_cgpa)
            st.warning(
                f"Modified Block #{block_idx} without re-mining. "
                "The active ledger should now fail verification."
            )
            st.rerun()
    else:
        st.info("Issue at least one manual certificate to test tampering.")

    if synthetic_mode:
        if st.button("Reset Synthetic Ledger", use_container_width=True):
            dataset = load_synthetic_dataset()
            st.session_state.synthetic_chain = create_chain_from_records(
                dataset["records"]
            )
            st.rerun()
    else:
        if st.button("🔄 Reset Manual Blockchain", use_container_width=True):
            st.session_state.manual_chain = [create_genesis_block()]
            st.rerun()


# Only the selected ledger is audited and shown.
active_chain = (
    st.session_state.synthetic_chain
    if st.session_state.synthetic_mode
    else st.session_state.manual_chain
)

if st.session_state.synthetic_mode:
    st.info(
        "🧪 **SYNTHETIC DATA MODE ACTIVE** — showing fictional repository records. "
        "Manual records are kept separately."
    )

is_valid, broken_blocks = audit_chain(active_chain)

if is_valid:
    if len(active_chain) == 1:
        st.info("ℹ️ **LEDGER READY:** Genesis block created. No certificates issued yet.")
    else:
        st.success(
            "✅ **BLOCKCHAIN AUDIT PASSED:** All displayed blocks pass the current "
            "hash and chain-link integrity checks."
        )
else:
    st.error(
        "🚨 **SECURITY ALERT — TAMPERING DETECTED!** "
        "A cryptographic hash mismatch or broken chain link was found."
    )

st.subheader("Live Blockchain Explorer")
ledger_label = "Synthetic demonstration ledger" if st.session_state.synthetic_mode else "Manual ledger"
st.caption(f"{ledger_label} • {len(active_chain)} blocks")

for block in active_chain:
    tampered = block.index in broken_blocks
    block_status = "🔴 COMPROMISED BLOCK" if tampered else "🟢 VERIFIED BLOCK"

    with st.container(border=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"### Block #{block.index} ({block_status})")
            st.write(f"**Student:** {block.certificate_data['student_name']}")
            st.write(
                f"**Roll No:** `{block.certificate_data['roll_no']}` "
                f"| **Course:** {block.certificate_data['course']}"
            )
            st.write(f"**Recorded CGPA:** `{block.certificate_data['cgpa']}`")
        with col2:
            st.write(f"**Timestamp:** {block.timestamp} | **PoW Nonce:** `{block.nonce}`")
            st.code(
                f"Previous Hash : {block.previous_hash}\n"
                f"Stored Hash   : {block.hash}\n"
                f"Actual Hash   : {block.calculate_hash()}",
                language="text",
            )
