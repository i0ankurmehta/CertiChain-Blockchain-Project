# EACT-B3 Experiment Protocol — Provenance and Freshness

**Version:** 1.0  
**Dataset:** Synthetic scenarios only  
**Application:** CertiChain / EACT-B3 Provenance & Freshness Lab

## Research question

Can a credential-verification workflow distinguish:
1. a valid hash comparison from a trustworthy reference hash;
2. a previously authenticated issuer from one whose authentication evidence is stale;
3. a current status response from an old or unauthenticated status claim?

## Motivation

EACT-B2 showed that a single disposition can hide simultaneous findings. EACT-v2 improved this by retaining multiple findings. B3 examines whether each finding has an identifiable source and a usable timestamp.

## Experimental policy parameters

The prototype uses:
- **Issuer-authentication evidence:** maximum age of 90 days.
- **Credential-status evidence:** maximum age of 24 hours.

These are explicit experimental defaults only. They are not universal standards or claims about any university, issuer, or legal requirement. Real thresholds must be set with the relevant issuer, credential type, status-update frequency, and verification purpose.

## Evidence dimensions

| Dimension | Metadata recorded |
|---|---|
| Reference-hash provenance | Origin and signature-verification state |
| Issuer authentication | Authentication state, trusted source, age in days |
| Credential status | Status value, source type, source authentication, age in hours |
| Integrity result | Match, mismatch, or not checked |

## Predefined scenario suite

The ten synthetic fixtures in `EACT_B3_provenance_scenarios.json` test:
- fresh authenticated issuer with a revoked status;
- stale issuer-authentication evidence;
- matching hash with unknown reference origin;
- stale credential-status snapshot;
- invalid reference signature;
- untrusted source claiming revocation;
- missing issuer-authentication timestamp;
- all-current positive control;
- mismatch against trusted signed reference;
- issuer and status evidence both stale.

## Procedure

1. Open **EACT-B3 — Provenance & Freshness Lab** from the Streamlit page navigation.
2. Select each B3 case in turn.
3. Confirm the default evidence values match the fixture.
4. Record the primary disposition and all independent findings.
5. Change selected metadata values to test threshold boundaries and source trust.
6. Record any difference from the authored fixture expectation in the results CSV.
7. Do not enter real student or institutional data.

## Measures

- Fixture-conformance count (software behaviour versus authored expected outputs).
- Correct distinction between reference hash match and reference provenance.
- Correct distinction between authenticated and stale issuer evidence.
- Correct handling of current, stale, missing-timestamp, and unauthenticated status evidence.
- Whether all simultaneous provenance/freshness issues are surfaced as findings.

## Limitations

- Synthetic categorical values and ages only; no external API or trust anchor.
- The prototype does not perform cryptographic signature verification.
- Source labels in the fixtures are assumed by the rule engine; they are not independently authenticated.
- The 90-day and 24-hour thresholds are not externally validated.
- Fixture conformance is not real-world fraud detection accuracy, issuer acceptance, or employer decision quality.
- A production system would need issuer-specific policy, auditable trust anchors, signed timestamped evidence, revocation/status semantics, key rotation, privacy controls, and authorised integrations.
