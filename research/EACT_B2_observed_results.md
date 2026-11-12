# EACT-B2 Observed Results: Conflicting Evidence and Rule Precedence

**Study:** Evidence-Aware Credential Triage (EACT-v1)
**Environment:** User-operated local Streamlit Evidence Triage Lab
**Screenshot date shown:** 13 November 2026
**Evidence source:** User-supplied screenshots
**Data:** Fictional scenarios manually selected in the lab.

## Summary

The screenshots show five of the seven planned B2 configurations exactly. Two additional captures show related but misconfigured variants: issuer identity was left as unknown where the protocol required authenticated. Those variants are documented separately and are not counted as successful executions of B2-04 and B2-05.

## Planned cases with matching configurations

| Case | Configured inputs | Observed EACT output | Assessment |
|---|---|---|---|
| B2-01 | mismatch / unknown / unknown / not_checked / service_unavailable | Altered — integrity mismatch | Matches current rule-order prediction. Integrity mismatch is checked before source availability. |
| B2-02 | match / authenticated / revoked / mismatch / status_source_available | Revoked | Matches prediction. Revoked status is returned before subject mismatch is evaluated. |
| B2-03 | match / unknown / revoked / mismatch / status_source_available | Issuer unverified | Matches prediction. Unknown issuer is returned before revoked status and subject mismatch. |
| B2-06 | mismatch / unknown / unknown / not_checked / consent_pending | Altered — integrity mismatch | Matches prediction. Integrity mismatch is evaluated before pending consent. |
| B2-07 | not_checked / unknown / unknown / not_checked / consent_pending | Pending — consent required | Matches prediction. With no integrity mismatch, pending consent is returned. |

**Exact planned configurations observed: 5/7.** This is not a 5/7 model-accuracy result; it is the count of planned configurations visibly set in supplied screenshots and yielding the expected current-code output.

## Related configuration variants captured

### Variant related to B2-04 — subject mismatch with issuer left unknown

Observed configuration: integrity match; issuer unknown; status active; subject mismatch; source available.

Observed output: **Issuer unverified**.

This is consistent with the current first-match code because issuer authentication is checked before subject mismatch. However, it is not planned B2-04, which requires issuer identity authenticated. B2-04 remains untested.

### Variant related to B2-05 — status endpoint unavailable with issuer left unknown

Observed configuration: integrity match; issuer unknown; status unknown; subject match; source status_service_unavailable.

Observed output: **Inconclusive — source unavailable**.

This is consistent with the current code because its special partial-verification path requires the issuer to be authenticated. It is not planned B2-05. B2-05 remains untested until issuer identity is authenticated, with the other fields unchanged.

## What the observed rule precedence reveals

1. **Integrity mismatch dominates workflow availability.** In B2-01 and B2-06, the system returns altered even when the source is unavailable or consent is pending. This is only defensible when the mismatch is based on a trusted reference digest or signature comparison. The UI does not separately model provenance of the reference used for comparison.
2. **Issuer uncertainty hides other signals in the primary label.** In B2-03, the result is issuer unverified, although the configured state also contains a revoked status and subject mismatch. Those signals are not surfaced by the current single-disposition output.
3. **Revocation hides a subject mismatch in the primary label.** In B2-02, the output is revoked while subject mismatch is also configured. The reviewer receives the primary status but not a complete findings list.
4. **Unknown issuer changes the unavailable-status result.** The B2-05 variant returned generic source-unavailable, not partial verification, because issuer authentication was not supplied.

## Remaining exact cases

| Case | Status | Required setup |
|---|---|---|
| B2-04 | NOT YET TESTED | match / authenticated / active / mismatch / available |
| B2-05 | NOT YET TESTED | match / authenticated / unknown / match / status_service_unavailable |

## Research implication

The screenshots support investigating a richer EACT output: one primary disposition plus a list of all independently observed findings, with evidence provenance and authority clearly represented. They do not establish the best real-world precedence policy. That would require domain-expert review and testing with authorised, appropriately de-identified cases.

All observations are UI-level tests against manually selected synthetic evidence. They are not measurements of employer behaviour, real-world fraud prevalence, or verification accuracy.