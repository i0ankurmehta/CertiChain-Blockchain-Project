# EACT-B2 Complete Results: Conflicting Evidence and Rule Precedence

**Study:** Evidence-Aware Credential Triage (EACT-v1)  
**Environment:** User-operated local Streamlit Evidence Triage Lab  
**Date shown by screenshots:** 13 November 2026  
**Evidence:** Seven planned case configurations represented in user-supplied screenshots  
**Data:** Fictional, manually configured evidence only

## Summary

All seven B2 configurations were completed. The screenshots support the expected output for each case under the current EACT-v1 first-match rule order. The experiment demonstrates rule precedence and identifies where a single disposition hides simultaneous signals. It is not a real-world accuracy study or validation of the policy priorities.

| Case | Input combination | Observed output |
|---|---|---|
| B2-01 | mismatch / unknown / unknown / not_checked / service_unavailable | Altered — integrity mismatch |
| B2-02 | match / authenticated / revoked / mismatch / status_source_available | Revoked |
| B2-03 | match / unknown / revoked / mismatch / status_source_available | Issuer unverified |
| B2-04 | match / authenticated / active / mismatch / available | Subject mismatch |
| B2-05 | match / authenticated / unknown / match / status_service_unavailable | Partially verified — status unknown |
| B2-06 | mismatch / unknown / unknown / not_checked / consent_pending | Altered — integrity mismatch |
| B2-07 | not_checked / unknown / unknown / not_checked / consent_pending | Pending — consent required |

**Observed configuration coverage: 7/7 planned cases.** This is completion of the seven designed UI tests, not a 100% accuracy rate.

## Findings from rule precedence

1. **Integrity mismatch takes precedence over availability and consent.** B2-01 and B2-06 return Altered. This is only justified when the mismatch is based on a trusted reference comparison. The current evidence input does not independently model reference provenance.
2. **Issuer uncertainty hides other evidence in the primary label.** In B2-03, the inputs also include revoked status and subject mismatch, but the primary output is Issuer unverified.
3. **Revocation hides a simultaneous subject mismatch.** In B2-02, the primary output is Revoked; the subject mismatch is not surfaced in the single-result explanation.
4. **Subject mismatch is returned when issuer and status evidence are otherwise acceptable.** B2-04 returns Subject mismatch.
5. **An authenticated issuer can be partially verified while status remains unknown.** B2-05 returns Partially verified — status unknown when the status endpoint is unavailable.
6. **Pending consent is a workflow state, not a fraud finding.** B2-07 returns Pending — consent required.

## Research implication

The results justify prototyping an EACT-v2 output that keeps a primary disposition while also returning every independently observed finding. The output should identify the evidence basis for each finding and distinguish authenticated status evidence from unverified claims. This is a design hypothesis to be tested, not a universal policy.

## Limitations

- All seven cases are synthetic and manually configured.
- The experiment confirms current rule behaviour against designed cases; it does not measure real-world credential-verification accuracy.
- The five evidence dimensions are categorical inputs; the prototype does not connect to issuer registries or independently validate the asserted evidence.
- The experiment does not establish how employers should weigh or prioritise all conflicting evidence.
- Domain-expert review and authorised, appropriately de-identified cases would be required for external validation.
