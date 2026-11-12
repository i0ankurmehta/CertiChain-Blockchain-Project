# Experiment Protocol: CertiChain Integrity and Evidence-Triage Evaluation

**Protocol version:** 1.1  
**Dataset:** Synthetic only

## A. Functional experiment — current prototype

### Preconditions
- Use the merged application in a local Streamlit session.
- Use only fictional records.
- Keep the same browser/session open throughout A1–A4. The ledgers are held in Streamlit session state and are not durable storage.

### A1 — Clean synthetic baseline
1. Turn Synthetic Data Records ON.
2. Select Reset Synthetic Ledger.
3. Confirm blocks #0–#3 and inspect the audit.
**Observed:** Four of four blocks displayed verified. **PASS — screenshot evidence.**

### A2 — Tamper with first certificate
1. Keep Synthetic Data Records ON.
2. Target Block #1 (Rohan Sharma), change CGPA 8.6 to 9.9 without re-mining.
3. Click Tamper Database Record.
**Observed:** Block #1 stored/recalculated hashes mismatch. Blocks #1–#3 display compromised; blocks #2 and #3 have matching local hash values but are flagged through downstream trust propagation. Genesis remains verified. **PASS — screenshot evidence.**

### A3 — Reset and recovery
1. From the tampered state, click Reset Synthetic Ledger.
2. Confirm Rohan 8.6, Priya 9.1, Aman 7.4 and all four blocks verified.
**Observed:** User confirmed that all records and verified statuses returned. **PASS — user-confirmed; no dedicated post-reset screenshot.**

### A4 — Cross-mode isolation
1. Turn Synthetic Data Records OFF.
2. Issue Research Test Candidate / TEST-001 / CGPA 8.2.
3. Turn Synthetic Data Records ON and tamper with a synthetic record.
4. Turn Synthetic Data Records OFF again.
5. Confirm the manual test certificate remains in the manual ledger.
**Observed:** User confirmed that the manual record remained available and the two ledgers remained independent. **PASS — user-confirmed within the same session; not a persistence test.**

## B. Extended research experiment — mixed-evidence scenarios

### Objective
Compare a simple hash-only pass/fail interpretation with a proposed evidence-aware triage model using fictional credential cases.

### Scenario matrix
The fixtures in verification_scenarios.json cover a trusted registry match, altered content, unknown issuer, no registry record, unavailable source, revoked credential, subject mismatch, consent pending, expired credential, and unknown status.

### Proposed evaluation
1. **Baseline:** treat a matching hash as valid and a mismatching hash as invalid.
2. **EACT proposal:** preserve independent evidence dimensions: integrity, issuer identity, credential status, subject match, and source/consent state.

### Measures
- Correct disposition rate on the synthetic fixtures.
- False assurance: fully verified output despite missing or contradictory issuer/status/subject evidence.
- False fraud: fraud label assigned solely because a source is unavailable or consent is pending.
- Inconclusive/manual-review rate.
- Evidence completeness: number of dimensions explicitly reported.

These measures apply only to the designed synthetic scenarios; they do not represent a real-world fraud rate or actual employer behaviour.

## C. Data and privacy rules
- Use fictional names and identifiers only.
- Do not place personal identifiers or full student records on a public blockchain.
- Keep reasons for inconclusive outcomes visible.
- Collect only evidence needed for the verification purpose.
- Do not connect to institutional systems without explicit authorisation.