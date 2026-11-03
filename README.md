# CertiChain: Tamper-Proof Academic Certificate Ledger

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/i0ankurmehta/CertiChain-Blockchain-Project/blob/main/CertiChain.ipynb)

## Abstract
CertiChain is a lightweight, cryptographic blockchain ledger designed to secure university academic records. By utilizing SHA-256 hashing and Proof-of-Work (PoW) consensus, it prevents unauthorized grade alterations and document forgery.

## Problem Statement
Traditional university databases rely on centralized SQL servers where privileged administrators can silently modify student grades or degree records (`UPDATE students SET cgpa = 9.8`). CertiChain eliminates this vulnerability by chaining blocks cryptographically.

## System Architecture & Algorithm
* **Block Structure:** Index, Timestamp, Certificate Data (Name, Roll No, Course, CGPA), Previous Hash, Nonce, and Current Hash.
* **Proof-of-Work (PoW):** Requires finding a nonce that generates a SHA-256 hash starting with 3 leading zeros (`000...`), making ledger rewrites computationally prohibitive.
* **Tamper Detection Audit:** Iterates through the chain, recalculating hashes and validating previous hash links to instantly catch database tampering.

## Running the Web App
```bash
pip install -r requirements.txt
streamlit run app.py

eof
