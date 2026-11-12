# EACT Experiment B2 — Conflicting Evidence and Rule Precedence

**Version:** 1.1  
**Data:** Synthetic only

## Research question
When evidence dimensions conflict, does the current first-match decision preserve enough information for a reviewer, or can a single disposition hide simultaneous findings?

## Procedure
For each case, set all five sidebar controls in the local EACT lab exactly as listed. Record the disposition and explanation.

## Completed case matrix

| ID | Integrity | Issuer | Status | Subject | Source | Observed output |
|---|---|---|---|---|---|---|
| B2-01 | mismatch | unknown | unknown | not_checked | service_unavailable | Altered |
| B2-02 | match | authenticated | revoked | mismatch | status_source_available | Revoked |
| B2-03 | match | unknown | revoked | mismatch | status_source_available | Issuer unverified |
| B2-04 | match | authenticated | active | mismatch | available | Subject mismatch |
| B2-05 | match | authenticated | unknown | match | status_service_unavailable | Partially verified — status unknown |
| B2-06 | mismatch | unknown | unknown | not_checked | consent_pending | Altered |
| B2-07 | not_checked | unknown | unknown | not_checked | consent_pending | Pending — consent required |

**Result:** All seven planned UI configurations were completed and the observed outputs matched the current rule-order predictions. This is test-case completion, not real-world accuracy.

## Analysis
- Integrity mismatch takes precedence over source/consent workflow states.
- Issuer uncertainty takes precedence over a reported revoked status and subject mismatch.
- Revocation takes precedence over a simultaneous subject mismatch in the primary result.
- An authenticated issuer with unavailable status can be partially verified, with status explicitly unknown.
- Pending consent remains a workflow state, not a fraud finding.

## Next design hypothesis
Prototype a multi-finding response: retain a primary disposition, but also show all independently observed findings, their evidence basis and whether the evidence source is authenticated. Test it against the same seven conflict cases before replacing EACT-v1.

## Limits
Synthetic inputs only; no registry/API integration; no real employer decision-making or fraud accuracy measured. The experiment tests software rule behaviour, not normative policy correctness.
