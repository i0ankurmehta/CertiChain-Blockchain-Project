import streamlit as st
import hashlib
import json
from datetime import datetime

st.set_page_config(page_title="CertiChain - University Ledger", layout="wide")

class CertificateBlock:
    def __init__(self, index, student_name, roll_no, course, cgpa, previous_hash):
        self.index = index
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.certificate_data = {
            "student_name": student_name,
            "roll_no": roll_no,
            "course": course,
            "cgpa": float(cgpa)
        }
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_content = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "certificate_data": self.certificate_data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_content.encode()).hexdigest()

    def mine_block(self, difficulty=3):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

if "chain" not in st.session_state:
    genesis = CertificateBlock(0, "GENESIS_BLOCK", "0000", "System Init", 0.0, "0" * 64)
    genesis.mine_block(3)
    st.session_state.chain = [genesis]

st.title("🎓 CertiChain: Tamper-Proof Academic Certificate Ledger")
st.caption("SHA-256 & Proof-of-Work Blockchain Demonstration for College Viva")

with st.sidebar:
    st.header("1. Issue New Certificate")
    with st.form("issue_form", clear_on_submit=True):
        name = st.text_input("Student Name", placeholder="e.g., Rohan Sharma")
        roll = st.text_input("Roll Number", placeholder="e.g., BCA2401")
        course = st.selectbox("Course", ["BCA Cybersecurity", "BCA Data Science", "BCA Cloud Tech", "MCA"])
        cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, value=8.5, step=0.1)
        submitted = st.form_submit_button("⛏️ Mine & Issue Certificate")
        
        if submitted and name and roll:
            prev_block = st.session_state.chain[-1]
            new_block = CertificateBlock(len(st.session_state.chain), name, roll, course, cgpa, prev_block.hash)
            new_block.mine_block(3)
            st.session_state.chain.append(new_block)
            st.success(f"Block #{new_block.index} Mined!")

    st.divider()
    st.header("2. 🚨 Simulate Hacker Attack")
    if len(st.session_state.chain) > 1:
        block_idx = st.number_input("Target Block #", min_value=1, max_value=len(st.session_state.chain)-1, step=1)
        fake_cgpa = st.number_input("Inject Fake CGPA", min_value=0.0, max_value=10.0, value=9.9, step=0.1)
        if st.button("Tamper Database Record"):
            st.session_state.chain[block_idx].certificate_data["cgpa"] = float(fake_cgpa)
            st.warning(f"Modified Block #{block_idx} CGPA without re-mining!")
    else:
        st.info("Issue at least 1 certificate to test tampering.")

    if st.button("🔄 Reset Blockchain"):
        del st.session_state.chain
        st.rerun()

is_valid = True
broken_blocks = set()

for i in range(1, len(st.session_state.chain)):
    curr = st.session_state.chain[i]
    prev = st.session_state.chain[i - 1]
    if curr.hash != curr.calculate_hash() or curr.previous_hash != prev.hash or i - 1 in broken_blocks:
        is_valid = False
        broken_blocks.add(i)

if is_valid:
    st.success("✅ **BLOCKCHAIN AUDIT PASSED:** All certificates are cryptographically verified and untampered.")
else:
    st.error("🚨 **SECURITY ALERT — TAMPERING DETECTED!** Cryptographic hash mismatch found in the ledger.")

st.subheader("Live Blockchain Explorer")
for b in st.session_state.chain:
    tampered = b.index in broken_blocks
    border_status = "🔴 COMPROMISED BLOCK" if tampered else "🟢 VERIFIED BLOCK"
    with st.container(border=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"### Block #{b.index} ({border_status})")
            st.write(f"**Student:** {b.certificate_data['student_name']}")
            st.write(f"**Roll No:** `{b.certificate_data['roll_no']}` | **Course:** {b.certificate_data['course']}")
            st.write(f"**Recorded CGPA:** `{b.certificate_data['cgpa']}`")
        with col2:
            st.write(f"**Timestamp:** {b.timestamp} | **PoW Nonce:** `{b.nonce}`")
            st.code(f"Previous Hash : {b.previous_hash}\nStored Hash   : {b.hash}\nActual Hash   : {b.calculate_hash()}", language="text")
