# EACT-B3 Observed Results — Provenance and Freshness

**Experiment:** EACT-B3  
**Application:** CertiChain — Provenance Freshness Lab  
**Evidence:** Four user-supplied screenshots from the local Streamlit UI  
**Scenario coverage:** B3-01 through B3-04  
**Data:** Synthetic/manual only

## Summary

The first four planned B3 scenarios were run in the local UI. Each screenshot shows the original fixture values and a primary disposition matching the expected disposition in the scenario fixture.

**Observed fixture conformance: 4/4 for the four captured scenarios.** This is not a real-world accuracy measurement. Scenarios B3-05 through B3-10 remain to be tested.

## Observations

| Case | Key observed input | UI result | Assessment |
|---|---|---|---|
| B3-01 | Trusted signed issuer manifest; issuer authentication 2 days old; authenticated status API says revoked; status age 1 hour | Credential status confirmed: revoked; both freshness indicators Current | Matches fixture expectation |
| B3-02 | Trusted signed manifest; issuer authentication 180 days old; status age 1 hour | Issuer-authentication evidence stale; issuer freshness Stale, status freshness Current | Matches fixture expectation |
| B3-03 | Hash match, but reference origin unknown and reference signature not checked; issuer and status freshness current | Reference provenance unverified | Matches fixture expectation |
| B3-04 | Trusted registry export with verified reference; issuer authentication 4 days old; signed status snapshot 1080 hours (45 days) old | Credential-status evidence stale; issuer freshness Current, status freshness Stale | Matches fixture expectation |

## Interpretation

### B3-01 — Fresh source can still report a negative status

The system did not treat freshness as equivalent to a positive credential outcome. The issuer/status evidence was current, and the supplied authenticated source reported the credential as revoked. The application therefore returned a confirmed revoked status in this synthetic case.

### B3-02 — Past authentication is not automatically current authentication

The issuer-authentication evidence was 180 days old, beyond the configured 90-day experimental threshold. The app surfaced a stale issuer-authentication finding while the status evidence remained current.

### B3-03 — Matching a hash does not establish the reference's origin

The document comparison matched, but the reference origin was unknown and its signature had not been checked. The app correctly refused to treat the reference as trusted. This illustrates why a digest comparison needs a trustworthy reference.

### B3-04 — Status freshness is distinct from issuer freshness

The issuer authentication was only four days old, while the status snapshot was 1080 hours old. The app flagged status evidence as stale without incorrectly labelling the issuer authentication stale.

## Threshold note

The app currently uses a maximum issuer-authentication age of 90 days and maximum credential-status age of 24 hours. These are explicit experimental defaults for B3, not universal standards. The appropriate values would depend on issuer policy, credential type, status-change frequency, and verification context.

## Limitations

- The screenshots show manually selected synthetic fixture metadata.
- The application does not independently verify digital signatures, issuer-directory records, timestamps, registry exports, or status endpoints.
- The labels such as trusted issuer directory and signed registry snapshot are scenario assumptions, not independently established trust anchors.
- Four of ten scenarios have been captured. The remaining six must be run before the full B3 experiment can be described as complete.
- Fixture conformance establishes that the code returns its authored expected results; it does not establish real-world verification accuracy or policy suitability.
