# Experiment Log: A1–A4 Functional Evaluation

**Study:** Evidence-Aware Academic Credential Verification (EACT-v1)  
**Application:** CertiChain / EREBUS_v027  
**Environment:** Local Streamlit application at http://localhost:8501  
**Date shown by application:** 12–13 November 2026  
**Dataset:** Repository synthetic dataset; all records fictional  
**Evidence source:** User-supplied screenshots for A1/A2; explicit user confirmation for A3/A4

## A1 — Clean synthetic baseline

Synthetic Data Records was enabled. The synthetic ledger contained four blocks: one genesis block and three certificate blocks.

| Block | Record | Observed status |
|---|---|---|
| #0 | GENESIS_BLOCK | Verified |
| #1 | Rohan Sharma — BCA2401 | Verified |
| #2 | Priya Patel — BCA2402 | Verified |
| #3 | Aman Verma — BCA2403 | Verified |

The application displayed a successful audit banner. Stored and recalculated hashes shown for the captured blocks matched. Displayed proof-of-work nonces were Genesis 5108, Rohan 2691, Priya 11590 and Aman 924.

**A1 outcome: PASS.** Four of four displayed blocks were marked verified in the captured clean baseline.

## A2 — Controlled tampering of Block #1

The attack controls targeted Block #1 (Rohan Sharma). The displayed CGPA was changed from **8.6 to 9.9** without re-mining the block.

| Block | Record | Observed status | Interpretation |
|---|---|---|---|
| #0 | GENESIS_BLOCK | Verified | Genesis record remained unchanged. |
| #1 | Rohan Sharma — BCA2401 | Compromised | Stored and recalculated hashes differed after the CGPA change. |
| #2 | Priya Patel — BCA2402 | Compromised | Its own stored and recalculated hash still matched, but it was flagged as a downstream descendant of a compromised block. |
| #3 | Aman Verma — BCA2403 | Compromised | Its own stored and recalculated hash still matched, but it was flagged as a downstream descendant of a compromised block. |

For Block #1, the stored hash began 000619d..., while the recalculated hash began c1abdb.... The application displayed Rohan's modified CGPA as 9.9.

**A2 outcome: PASS.** The controlled change was detected, the altered block was flagged, and the application marked subsequent blocks as compromised.

### A2 interpretation

Two separate audit behaviours were observed:
1. **Direct content-integrity failure:** Block #1's recalculated hash differed from its stored hash.
2. **Downstream trust invalidation:** Blocks #2 and #3 were marked compromised because an earlier block in their chain was compromised, even though their own local hash recalculations still matched their stored hashes.

It would be incorrect to claim that all three certificate records were independently modified. The screenshots support one direct record alteration and two downstream trust-invalidated blocks.

## A3 — Reset and recovery after tampering

After the A2 tampering state, the user selected **Reset Synthetic Ledger**.

**User-reported observation:** The synthetic ledger rebuilt from the repository dataset. Rohan's CGPA returned to 8.6, Priya's to 9.1, and Aman's to 7.4. Genesis and all three certificate blocks returned to the verified state.

**A3 outcome: PASS (user-confirmed).** No dedicated post-reset screenshot was supplied; this result is recorded from the user's explicit confirmation.

## A4 — Manual/synthetic ledger isolation

The user switched Synthetic Data Records OFF, issued the instructed manual test certificate (Research Test Candidate / TEST-001 / CGPA 8.2), switched synthetic mode ON and performed the synthetic tampering test, then switched synthetic mode OFF again.

**User-reported observation:** The manual test certificate remained available in the manual ledger after returning from the synthetic ledger. The manual and synthetic modes behaved independently.

**A4 outcome: PASS (user-confirmed).** This supports separation of the two Streamlit session-state ledgers within the same session. It does not establish persistence across browser-session loss or a server/application restart.

## Updated test summary

| Test | Result | Evidence provenance |
|---|---|---|
| A1 — clean synthetic baseline | PASS | User screenshots |
| A2 — controlled Block #1 tampering | PASS | User screenshots |
| A3 — reset and recovery | PASS | User confirmation; no dedicated post-reset screenshot |
| A4 — manual/synthetic isolation | PASS | User confirmation; no dedicated before/after screenshot pair |

## Limitations of this experiment

- It does not establish issuer authenticity, student identity, or credential ownership.
- It does not measure detection latency, throughput, scalability, or real-world fraud rates.
- It does not prove resistance to an attacker who can rewrite and re-mine the entire local chain.
- It does not demonstrate a distributed consensus network.
- It tests mode isolation only within one active Streamlit session; both ledgers remain in session memory.
- It does not establish how actual employers make hiring decisions.

The observations are from a user-operated local run, not an independent laboratory replication. Preserve the original screenshots and this log together for later review.