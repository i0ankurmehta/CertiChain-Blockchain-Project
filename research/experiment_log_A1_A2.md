# Experiment Log: A1 Baseline and A2 Controlled Tampering

**Study:** Evidence-Aware Academic Credential Verification (EACT-v1)  
**Application:** CertiChain / EREBUS_v027  
**Environment:** Local Streamlit application at `http://localhost:8501`  
**Date shown by application:** 12 November 2026  
**Dataset:** Repository synthetic dataset; all records fictional  
**Evidence source:** User-supplied screenshots from the local test session

## A1 — Clean synthetic baseline

### Setup
Synthetic Data Records was enabled. The synthetic ledger contained four blocks: one genesis block and three certificate blocks.

### Observed result

| Block | Record | Observed status |
|---|---|---|
| #0 | GENESIS_BLOCK | Verified |
| #1 | Rohan Sharma — BCA2401 | Verified |
| #2 | Priya Patel — BCA2402 | Verified |
| #3 | Aman Verma — BCA2403 | Verified |

The application displayed a successful audit banner. The stored and recalculated hashes shown for the visible blocks matched. The displayed proof-of-work nonces were:

- Genesis: 5108
- Rohan: 2691
- Priya: 11590
- Aman: 924

**A1 outcome: PASS.** Four of four displayed blocks were marked verified in the captured clean baseline.

## A2 — Controlled tampering of Block #1

### Intervention
The attack controls targeted Block #1 (Rohan Sharma). The displayed CGPA was changed from **8.6 to 9.9** without re-mining the block.

### Observed result

| Block | Record | Observed status | Interpretation |
|---|---|---|---|
| #0 | GENESIS_BLOCK | Verified | Genesis record remained unchanged. |
| #1 | Rohan Sharma — BCA2401 | Compromised | Stored hash and recalculated hash differed after the CGPA change. |
| #2 | Priya Patel — BCA2402 | Compromised | Its own stored and recalculated hash still matched, but it was flagged as a downstream descendant of a compromised block. |
| #3 | Aman Verma — BCA2403 | Compromised | Its own stored and recalculated hash still matched, but it was flagged as a downstream descendant of a compromised block. |

The application displayed a security-alert banner. For Block #1, the stored hash began with `000619d...`, while the recalculated hash began with `c1abdb...`. The CGPA displayed for Rohan was 9.9. The downstream blocks retained matching local stored/recalculated hash values in the screenshots but were classified as compromised by the audit's predecessor-compromise propagation rule.

**A2 outcome: PASS.** The controlled change was detected, the altered block was flagged, and the application marked its downstream blocks as compromised.

## Interpretation

The observed result demonstrates two distinct audit behaviours:

1. **Direct content-integrity failure:** Block #1's recalculated hash differed from its stored hash.
2. **Downstream trust invalidation:** Blocks #2 and #3 were marked compromised because an earlier block in their chain was compromised, even though their own local hash recalculations still matched their stored hashes.

This distinction must be preserved in the research reporting. It would be incorrect to state that all three certificate records were independently modified. The screenshot evidence supports one direct record alteration and two downstream trust-invalidated blocks.

## What this experiment does not establish

- It does not establish issuer authenticity or ownership of the credential.
- It does not measure detection latency, throughput, scalability, or real-world fraud rates.
- It does not prove resistance to an attacker who can rewrite and re-mine the entire local chain.
- It does not demonstrate a distributed consensus network.
- It does not establish how actual employers make hiring decisions.

## Pending tests

| Test | Status |
|---|---|
| A1 — clean synthetic baseline | PASS |
| A2 — controlled Block #1 tampering | PASS |
| A3 — reset and recovery after tampering | PENDING EVIDENCE |
| A4 — manual/synthetic ledger isolation under tampering | PENDING EVIDENCE |

## Evidence record

The screenshots supplied for this log show:
- the clean four-block baseline with green verified statuses;
- the red security alert after the Block #1 CGPA change;
- Genesis remaining green;
- Blocks #1–#3 marked compromised;
- the local stored/recalculated hash values used for the interpretation above.

Retain the original screenshots with the research materials. The observations above are based on those images, not on a fresh independent execution by the author of this log.
