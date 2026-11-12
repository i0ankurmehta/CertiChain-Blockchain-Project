# EACT-v1 Local UI Smoke-Test Observations

**Application:** CertiChain — Evidence-Aware Credential Triage Lab  
**Environment:** User-operated local Streamlit session at `http://localhost:8501/Evidence_Triage_Lab`  
**Date shown by the supplied screenshots:** 13 November 2026  
**Scenario data:** Fictional fixtures only  
**Evidence provenance:** User-supplied screenshots

## Observed cases

| Case | Evidence configured | Hash-only baseline | EACT output | Observation |
|---|---|---|---|---|
| EACT-01 — Official registry match | Integrity match; issuer authenticated; status active; subject match; source available with consent | VALID (hash matches) | Verified against trusted source | Positive control: all five dimensions assessed. |
| EACT-03 — Hash matches but issuer is unknown | Integrity match; issuer unknown; status unknown; subject not checked; offline document only | VALID (hash matches) | Issuer unverified | Demonstrates why a matching digest alone must not be described as issuer authentication. |
| EACT-05 — Verification source unavailable | Integrity match; issuer unknown; status unknown; subject match; source unavailable | VALID (hash matches) | Inconclusive — source unavailable | The system does not infer fraud solely from verification-source unavailability. |

## Scenario matrix display

The supplied screenshot of the scenario matrix displays all ten predefined cases (EACT-01 to EACT-10) with the “Matches predefined rule” indicator checked for every row.

**Observed UI fixture-conformance display: 10/10.**

This means the EACT rule function returned the predefined expected disposition for each of the ten synthetic scenario fixtures in the displayed application. It is a deterministic rule-conformance check against authored test expectations. It is not:
- a measured real-world verification accuracy rate;
- a study of actual employer decisions;
- proof that the expected labels are universally correct;
- an independent validation against real credential fraud cases.

## Interpretation

The clearest comparison is EACT-03 and EACT-05. The hash-only baseline reports “VALID (hash matches)” in both cases. EACT retains the uncertainty:
- EACT-03: issuer identity is not authenticated.
- EACT-05: the source is unavailable, so issuer/status evidence cannot be confirmed.

This supports the design rationale for separating document integrity from issuer identity and source availability. Further evaluation should include human review of the scenario labels, additional edge cases, unit tests, and eventually an authorised external-source pilot. No live NAD, DigiLocker, university, or training-provider endpoint was connected.
