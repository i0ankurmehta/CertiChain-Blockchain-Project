# Experiment Log — CertiChain Research

## Run A2: Synthetic certificate tampering and downstream trust propagation

**Recorded:** 12 November 2026, approximately 22:42–22:44 local time (Asia/Kolkata)  
**Application:** CertiChain Streamlit local run at `localhost:8501`  
**Dataset:** Repository synthetic dataset, version 1.0  
**Configuration:** Synthetic Data Records ON; four blocks total; proof-of-work difficulty 3  
**Evidence source:** User-provided screenshots captured during the run. Screenshots were reviewed in the research conversation; raw image files are not included in this repository commit.

### Objective

Test whether a post-issuance change to a synthetic certificate is detected by the integrity audit and whether the implementation marks later blocks as compromised when their trust depends on an altered predecessor.

### Baseline observation

Before tampering, the application displayed four blocks:

| Block | Record | CGPA | Displayed status |
|---|---|---:|---|
| #0 | GENESIS_BLOCK | 0.0 | VERIFIED |
| #1 | Rohan Sharma (BCA2401) | 8.6 | VERIFIED |
| #2 | Priya Patel (BCA2402) | 9.1 | VERIFIED |
| #3 | Aman Verma (BCA2403) | 7.4 | VERIFIED |

The application banner reported that the current hash and chain-link integrity checks passed for all displayed blocks.

### Intervention

The tester selected Block #1 and changed Rohan Sharma's recorded CGPA from **8.6 to 9.9** through the application's **Tamper Database Record** control, without re-mining the block.

### Observed result

| Block | Displayed status after intervention | Observation |
|---|---|---|
| #0 — Genesis | VERIFIED | Genesis hash remained unchanged. |
| #1 — Rohan Sharma | COMPROMISED | Stored hash and recalculated hash differed. |
| #2 — Priya Patel | COMPROMISED | Its own stored and recalculated hashes still matched, but it was marked compromised because it follows a compromised block. |
| #3 — Aman Verma | COMPROMISED | Its own stored and recalculated hashes still matched, but it was marked compromised through downstream trust propagation. |

The global application banner changed from a green audit-passed message to a red security alert reporting a cryptographic hash mismatch or broken chain link.

### Result against the test expectation

**PASS — controlled alteration detected.**

The implementation detected the modified data in Block #1 and propagated compromised status to Blocks #2 and #3. The screenshots show the intended distinction between a block whose own content hash mismatches and later blocks whose local content hashes still match but whose place in the chain is no longer treated as trusted.

### What this experiment establishes

For this controlled synthetic run, the application detects a changed field in a previously mined block and does not continue presenting later blocks as fully trusted.

### What this experiment does not establish

- It does not establish resistance to an attacker who can rewrite and re-mine the entire local chain.
- It does not authenticate the university or training provider that supposedly issued a credential.
- It does not establish subject identity, credential status, revocation status, or source availability.
- It is not a measurement of throughput, scalability, cryptographic strength, or real-world fraud detection.
- It is not evidence from real university records.

### Reset and recovery

A post-attack clean-state screenshot was not included in the evidence set for this A2 run. Reset functionality was separately reported as working in the earlier local feature test, but a clean recovery state should be captured as Experiment A3 evidence before it is counted in the formal results table.

### Evidence to retain

- Screenshot: clean four-block baseline and green audit banner.
- Screenshot: tampering alert and Genesis / Block #1 statuses.
- Screenshot: lower ledger showing Blocks #1, #2 and #3 marked compromised.

### Research interpretation

The observation supports the limited claim that CertiChain's current hash-and-link audit can detect this injected change and propagate a compromised state to dependent blocks in the tested four-block chain. It motivates the next investigation: how should a verifier report evidence that is incomplete even when document integrity checks pass?
