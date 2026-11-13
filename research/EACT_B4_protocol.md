# EACT-B4 Experiment Protocol — Trust Anchor Governance and Evidence Lifecycle

**Version:** 1.0  
**Dataset:** Synthetic scenarios only  
**Application:** CertiChain / EACT-B4 Trust Anchor Lifecycle Lab  
**Assessment fixture time:** 2026-11-13T00:00:00Z

## 1. Research question

How should a credential-verification system distinguish the current state of an issuer signing key from the historical validity of a credential signature, especially after routine rotation, expiry, revocation, or compromise?

A second question is whether a tamper-evident audit structure can make changes to trust-anchor and verification records detectable.

## 2. Motivation

EACT-B3 assessed source provenance and evidence freshness. B4 extends the work from evidence metadata to the lifecycle of the key that supports issuer authentication.

The design separates:
- anchor registration and trust status;
- key validity interval;
- lifecycle-event effective time;
- lifecycle-event recorded time;
- credential signing time;
- timestamp source and timestamp signature status;
- current key state;
- historical key state at signing;
- audit-record integrity.

A current key state should not automatically overwrite the meaning of a historical verification. Conversely, a historical signature must not be accepted solely because it was once recorded as valid if the relevant signing key was already compromised at signing time.

## 3. Standards context

This experiment is informed by, but does not claim conformance with, the following materials:

1. **NIST SP 800-57 Part 1 Rev. 5 (Final)** provides general key-management guidance, including lifecycle and compromise considerations. NIST's catalogue lists SP 800-57 Rev. 6 as an initial public draft, not a final publication, as checked for this experiment.
2. **RFC 5280**, especially the CRL invalidityDate extension, distinguishes the date a key is known or suspected to have been compromised from the date the CA processed the revocation. This motivates separate `effective_at` and `recorded_at` fields.
3. **RFC 6960 (OCSP)** defines `thisUpdate`, `nextUpdate`, `producedAt`, and revocation time semantics. This motivates recording the validity interval and time of status evidence rather than treating a status label as timeless.
4. **W3C Verifiable Credentials Data Model v2.0** provides the wider issuer-holder-verifier ecosystem context for digitally verifiable credentials.

References:
- NIST SP 800-57 Part 1 Rev. 5: https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final
- NIST SP 800-57 Rev. 6 Initial Public Draft: https://csrc.nist.gov/pubs/sp/800/57/pt1/r6/ipd
- RFC 5280: https://www.rfc-editor.org/rfc/rfc5280
- RFC 6960: https://www.rfc-editor.org/rfc/rfc6960
- W3C VC Data Model 2.0: https://www.w3.org/TR/vc-data-model/

## 4. Model

### 4.1 Trust anchor

A synthetic anchor record contains:
- key identifier and issuer identifier;
- public-key fingerprint label (synthetic);
- registration state;
- trusted-registry state;
- valid-from time;
- expiry time.

No private key material is stored in the prototype.

### 4.2 Lifecycle event

Events contain:
- event type: rotated, revoked, compromised, distrusted, or reinstated;
- effective time;
- recorded time;
- source category;
- authority state;
- event-signature state;
- reason.

Only events whose supplied source, authority state, and signature state match the prototype's configured trusted categories affect the authoritative key-state calculation. These fields are scenario assertions and are not independently authenticated by the app.

### 4.3 Historical verification

Verification records contain:
- credential ID;
- signature-check result;
- signed-at time;
- verified-at time;
- timestamp source;
- timestamp-token signature state.

A signing time is considered trusted in the prototype only when a recognised timestamp authority source and a verified timestamp signature are supplied. This is a deterministic fixture rule, not a cryptographic timestamp-token validator.

### 4.4 Audit chain

The application creates a hash-linked sequence of synthetic audit records. Each entry includes a sequence number, previous hash, event payload, and record hash.

A hash chain detects alteration of an entry when checked against an expected previous hash or trusted checkpoint. It does not prevent full-chain rewriting by an attacker who controls the storage and is not anchored by an independent checkpoint.

## 5. Predefined scenario suite

The ten fixtures test:
- B4-01: active key and current signature;
- B4-02: routine rotation after signature;
- B4-03: signature after rotation;
- B4-04: compromise effective before signing but recorded later;
- B4-05: trusted timestamp before later compromise;
- B4-06: expired key with provable pre-expiry historical signature;
- B4-07: signature after expiry;
- B4-08: unverified manual revocation claim;
- B4-09: unknown trust anchor;
- B4-10: compromise chronology with an untrusted client-clock timestamp.

The audit-chain test suite separately checks valid chains, record tampering, link tampering, sequence tampering, and an empty chain.

## 6. Procedure

1. Open the B4 Trust Anchor Lifecycle Lab page.
2. Select each B4 case.
3. Confirm the original fixture values are loaded.
4. Record primary disposition, current key state, historical key state at signing, and all independent findings.
5. Change an event or timestamp input and verify that the page marks the configuration as modified.
6. Use the audit-tampering checkbox to observe detection of an altered record.
7. Record outputs in `EACT_B4_results_template.csv` and compare the observed primary disposition with the expected fixture disposition.\n8. Distinguish trust-registry status from the date/event-derived key lifecycle state; a date-derived Active label does not establish issuer trust.\n9. Record audit-chain tampering separately from credential lifecycle findings.

## 7. Measures

- Fixture-conformance count (software output against authored expected output).
- Correct handling of routine rotation versus compromise.
- Correct ordering of effective time and recorded time.
- Whether trusted signing time is required for historical ordering.
- Whether expiry at signing is distinguished from expiry after signing.
- Whether unverified lifecycle claims remain unverified.
- Audit-chain detection of event-record alteration and hash-link tampering.

## 8. Limitations

- All fixtures are synthetic. No actual public/private keys or digital signature algorithms are exercised.
- The prototype trusts the fixture's categorical claims about registry, event source, authority and timestamp signature state.
- No live CRL, OCSP, issuer registry, trusted list, key directory or timestamp authority is connected.
- Historical signature decisions depend on issuer policy, timestamp semantics, compromise scope, revocation reason, and applicable law. The rule order here is a research hypothesis, not a universal certificate-validation policy.
- A hash-linked log is not immutable without independent checkpoints, protected storage, access controls, and governance.
- Ten fixture cases do not establish real-world security accuracy, cryptographic assurance, or readiness for institutional use.

## 9. Expected contribution

B4 tests whether the prototype can separate the key's present state from a historical signature's state at signing time, while preserving the chronology and provenance of lifecycle events. It also provides a first audit-chain tamper-detection demonstration. This prepares the research for later work on cryptographic trust anchors, independently verifiable signed events, archival signatures and governance approval workflows.


## 10. Observed results

All ten scenarios B4-01 through B4-10 were visually exercised in the local Streamlit UI using user-supplied screenshots. The observed primary dispositions matched the expected fixture dispositions (10/10 UI fixture conformance). The case-by-case results, lifecycle states, finding counts and limitations are documented in `EACT_B4_observed_results.md` and `EACT_B4_results_template.csv`. This is manual UI evidence against authored synthetic rules, not a real-world accuracy or cryptographic validation result.
