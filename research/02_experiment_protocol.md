# Experiment Protocol: CertiChain Integrity and Evidence-Triage Evaluation

**Protocol version:** 1.0  
**Research branch:** `research/mixed-credential-verification`  
**Dataset:** Synthetic only

## A. Immediate experiment — current prototype

### Objective
Verify that the merged Synthetic Ledger Mode behaves predictably under a clean baseline, a controlled alteration, reset, and a mode-isolation check.

### Preconditions
- Run the latest `main` branch or the research branch locally.
- Start Streamlit in one browser session.
- Do not use real student information.
- Keep the browser session open for the whole experiment; the manual ledger is currently held in Streamlit session state, not durable database storage.

### Test A1 — clean synthetic baseline
1. Turn **Synthetic Data Records** ON.
2. Select **Reset Synthetic Ledger**.
3. Confirm blocks #0–#3 are displayed.
4. Run/inspect the audit banner.
5. Record the block status, block count, and whether the hashes satisfy the displayed proof-of-work target.

**Expected:** Genesis plus three sample certificate blocks; all pass the current integrity audit.

### Test A2 — tamper with the first certificate
1. Keep Synthetic Data Records ON.
2. Select target Block #1 (Rohan Sharma).
3. Set Inject Fake CGPA to 9.9.
4. Click **Tamper Database Record**.
5. Record each block's status and the audit banner.

**Expected:** Block #1 is compromised because its recalculated hash differs from its stored hash. Blocks #2 and #3 are also treated as compromised downstream because their trust depends on the altered predecessor. Genesis remains verified.

### Test A3 — reset and recovery
1. Click **Reset Synthetic Ledger**.
2. Confirm the dataset is rebuilt from the repository JSON.
3. Record statuses again.

**Expected:** The synthetic chain returns to a clean state; all four blocks pass the audit.

### Test A4 — cross-mode isolation
1. Turn Synthetic Data Records OFF.
2. Issue a clearly synthetic manual test record, e.g. `Research Test Candidate` / `TEST-001`.
3. Turn Synthetic Data Records ON and tamper with Block #1.
4. Turn Synthetic Data Records OFF again.
5. Confirm the manual test record is still present and its ledger has not been affected.

**Expected:** Synthetic tampering affects only the synthetic chain. The manual chain remains unchanged within the same Streamlit session.

### Evidence to collect
- Screenshot of clean synthetic ledger.
- Screenshot of the tampering alert and block statuses.
- Screenshot after reset.
- Screenshot of manual record before and after synthetic-mode tampering.
- Record date/time, Git commit, branch, browser/session, and observations.

Do not report screenshots as performance measurements. This experiment tests functional behavior, not throughput or production security.

## B. Extended research experiment — mixed-evidence scenarios

### Objective
Compare a simple hash-only pass/fail interpretation with a proposed evidence-aware triage model using fictional credential cases.

### Scenario matrix
The scenario fixtures are in `verification_scenarios.json`. They include:
- trusted source + valid issuer evidence + active status;
- content/hash mismatch;
- intact document with issuer not authenticated;
- source has no matching record;
- source unavailable;
- revoked credential;
- subject/applicant mismatch;
- consent pending;
- expired credential;
- valid issuer signature but status unknown.

### Proposed evaluation
For each case, two decision rules are compared:

1. **Baseline:** treat a matching hash as 'valid' and a mismatching hash as 'invalid'.
2. **EACT proposal:** preserve the separate dimensions of integrity, issuer identity, status, subject match, and source/consent state; produce an evidence-based disposition.

### Primary measures
- **Correct disposition rate:** decisions matching the synthetic ground-truth label.
- **False assurance count:** cases labelled fully verified when issuer/status/subject evidence is missing or contradictory.
- **False fraud count:** cases labelled fraudulent solely because a registry/source is unavailable or consent is pending.
- **Inconclusive rate:** cases appropriately referred for review rather than forced into valid/invalid.
- **Evidence completeness:** number of relevant evidence dimensions explicitly reported.

### Important evaluation rule
The scenario fixtures define the expected outputs for a controlled test. They do not represent a measured real-world fraud rate or prove how actual employers behave. Results should be reported as performance on this synthetic test set only.

## C. Data and privacy rules
- Use fictional names and identifiers only.
- Do not place personal identifiers or full student records on a public blockchain.
- Keep the reason for an inconclusive result visible.
- Collect only evidence needed for the hiring decision.
- Do not connect to institutional systems without explicit authorisation.
