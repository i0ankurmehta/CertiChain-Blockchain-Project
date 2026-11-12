# EACT-B3 Complete Observed Results — Provenance and Freshness

**Experiment:** EACT-B3  
**Application:** CertiChain — Provenance Freshness Lab  
**Evidence:** Ten user-supplied screenshots from the local Streamlit UI, B3-01 through B3-10  
**Data:** Synthetic/manual only  
**Experimental parameters:** Issuer-authentication age <= 90 days; credential-status age <= 24 hours

## Summary

All ten planned B3 scenarios were exercised in the local UI. Each screenshot showed the selected fixture's original values, and the primary disposition matched the expected disposition authored in the fixture.

**Observed UI fixture conformance: 10/10.** This is completion of ten designed UI tests, not a real-world accuracy measurement, security certification, or validation of external issuers or registries.

## Complete result matrix

| Case | Main evidence condition | Observed primary disposition | Secondary findings / freshness |
|---|---|---|---|
| B3-01 | Current authenticated status source reports revoked | Credential status confirmed: revoked | Issuer Current; status Current |
| B3-02 | Issuer authentication 180 days old | Issuer-authentication evidence stale | Issuer Stale; status Current |
| B3-03 | Hash matches, reference origin unknown | Reference provenance unverified | Issuer Current; status Current |
| B3-04 | Status snapshot 1080 hours old | Credential-status evidence stale | Issuer Current; status Stale |
| B3-05 | Reference signature invalid | Reference provenance failed | Critical invalid-signature finding |
| B3-06 | Manual unauthenticated source claims revoked | Credential-status source untrusted | Inactive-status claim unconfirmed; status freshness Not Assessed |
| B3-07 | Issuer-authentication timestamp missing | Issuer-authentication freshness unknown | Issuer Timestamp Missing; status Current |
| B3-08 | All supplied evidence current and authenticated | Evidence provenance and freshness checks passed | Both Current; no findings |
| B3-09 | Mismatch against trusted signature-verified reference | Integrity mismatch against trusted reference | Issuer Current; status Current |
| B3-10 | Issuer authentication 180 days old; status snapshot 72 hours old | Issuer-authentication evidence stale | Both issuer and status freshness Stale; both findings displayed |

## Case-by-case interpretation

### B3-01 — Fresh evidence can still report a negative status
Both issuer authentication and credential-status evidence were within the configured freshness thresholds. The authenticated status source reported revoked. Freshness does not mean a credential is valid; it means the supplied evidence is recent enough under this prototype's chosen threshold.

### B3-02 — Previous issuer authentication can become stale
Issuer-authentication evidence was 180 days old, beyond the 90-day experimental threshold. The status record was one hour old and remained current. The system separated issuer-authentication freshness from status freshness.

### B3-03 — A matching digest does not establish reference provenance
The hash comparison matched, but the reference origin was unknown and signature verification was not checked. The system refused to treat the reference as trusted.

### B3-04 — Issuer freshness and status freshness are independent
Issuer authentication was four days old, while the signed status snapshot was 1080 hours old (45 days). The system flagged status evidence as stale without marking issuer authentication stale.

### B3-05 — An invalid reference signature blocks reliance on the reference
The source claimed to be an issuer-signed manifest, but the supplied signature-check result was invalid. The system returned Reference provenance failed and surfaced a critical finding. In a real implementation, signature validation must be performed cryptographically against a managed trust anchor; this prototype only evaluates the supplied categorical result.

### B3-06 — An unauthenticated revoked claim is not confirmed revocation
The source was a manual claim and was marked unverified. The system returned Credential-status source untrusted and separately listed the inactive-status claim as unconfirmed. Status freshness was Not Assessed because the source was not trusted. This avoids upgrading an unsupported claim into confirmed revocation.

### B3-07 — Authentication without a timestamp has unknown freshness
Issuer identity was marked authenticated, but its timestamp was unavailable. The system returned Issuer-authentication freshness unknown, while the credential-status evidence remained current. Evidence age cannot be calculated without a usable time reference.

### B3-08 — Positive control
The reference origin, signature status, issuer authentication and current status source satisfied the configured synthetic rules. Both freshness indicators were Current and no findings were raised. This is a positive software control, not external trust validation.

### B3-09 — Mismatch against a trusted reference
The reference was categorised as a trusted registry export and its signature status was supplied as verified. The document comparison reported mismatch. The system returned Integrity mismatch against trusted reference. The application did not itself verify the signature or source.

### B3-10 — Two independent freshness failures
Issuer authentication was 180 days old and the status snapshot was 72 hours old. The system displayed both stale findings. Its primary disposition was issuer-authentication evidence stale, while the findings table also preserved credential-status evidence stale.

## Cross-case findings

1. **Provenance precedes trust in a digest.** A hash match is not meaningful if the origin of the reference hash cannot be established.
2. **Freshness is dimension-specific.** Issuer-authentication and credential-status ages must be assessed independently.
3. **An unauthenticated status claim must remain a claim.** A manual revoked claim is not confirmed revocation.
4. **Missing timestamps create unknown freshness, not implicit currentness.**
5. **A primary disposition should not hide simultaneous findings.** B3-10 displays both stale issuer and stale status evidence.
6. **Fresh evidence can still support an adverse result.** B3-01 demonstrates that fresh evidence can confirm revoked status in the synthetic model.

## Threshold note

The implementation uses a maximum issuer-authentication age of 90 days and a maximum credential-status age of 24 hours. These are research parameters, not universal standards. Appropriate thresholds depend on issuer policy, credential type, status-change frequency, source guarantees and verification purpose.

## Limitations

- All screenshots represent synthetic/manual fixture inputs.
- The application does not independently verify signatures, issuer-directory records, timestamps, registry exports or status endpoints.
- Labels such as trusted issuer directory and signed registry snapshot are assumed scenario categories, not deployed trust anchors.
- The experiment tests ten predefined UI configurations and expected software outputs; it does not measure real-world verification accuracy, fraud detection or employer decision quality.
- The 90-day and 24-hour thresholds are not externally validated.
- A production system would require cryptographic trust-anchor management, signed and timestamped source responses, issuer-specific policy, key rotation, auditability, privacy controls and authorised integrations.

## Conclusion

EACT-B3 completed all ten synthetic UI scenarios with the expected primary dispositions. The experiment provides implementation-level evidence that the prototype separates reference provenance, issuer-authentication freshness and credential-status freshness, and can surface multiple independent findings. The next research stage should investigate trust-anchor governance and evidence lifecycle/auditability before real institutional integration is attempted.
