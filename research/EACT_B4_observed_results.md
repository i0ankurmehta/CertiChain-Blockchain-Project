# EACT-B4 Observed Results — Trust Anchor Governance and Evidence Lifecycle

**Experiment:** EACT-B4  
**Application:** CertiChain — Trust Anchor Lifecycle Lab  
**Scenario set:** B4-01 through B4-10  
**Evidence basis:** User-provided screenshots captured from the local Streamlit UI  
**Data type:** Synthetic/manual scenarios  
**Assessment fixture time:** 2026-11-13T00:00:00Z  
**Status:** 10/10 scenarios visually exercised; observed primary dispositions matched expected fixture dispositions

## 1. Summary

All ten predefined B4 scenarios were selected and exercised in the local application. The primary disposition visible in each supplied screenshot matched the expected disposition recorded in its synthetic fixture.

**Observed UI fixture conformance: 10/10.** This is manual visual confirmation of ten designed software scenarios. It is not a measurement of cryptographic accuracy, operational security, issuer trust, or real-world verification performance.

The experiment demonstrates a useful separation between:
- current key lifecycle state inferred from supplied validity dates and accepted lifecycle events;
- historical key lifecycle state at the asserted signing time;
- whether the signing timestamp is trusted by the prototype's configured source rule;
- whether the trust anchor itself is established by the configured registry assertion.

The screenshots also show the audit-chain alteration control detecting a deliberately changed record. In the B4-01 positive-control screenshot, the audit-tampering checkbox remained enabled, so the red audit-chain alert was active separately from the B4 lifecycle result (which showed zero lifecycle findings).

## 2. Complete observed result matrix

| Case | Scenario | Observed primary disposition | Current key lifecycle state | Key state at signing | Findings |
|---|---|---|---|---|---:|
| B4-01 | Active key and current credential signature | Active trust anchor — historical signature valid in prototype | Active | Active | 0 |
| B4-02 | Old key rotated after credential signing | Historical signature predates routine key rotation | Rotated | Pre-rotation | 1 |
| B4-03 | Credential signed after routine key rotation | Key was rotated before signing | Rotated | Rotated | 1 |
| B4-04 | Key compromise effective before signature, reported later | Key compromised at signing time | Compromised | Compromised | 2 |
| B4-05 | Historical signature predates later key compromise | Historical signature predates later key compromise | Compromised | Pre-compromise | 2 |
| B4-06 | Expired key, signature timestamped before expiry | Historical signature predates key expiry | Expired | Active | 0 |
| B4-07 | Credential signed after key expiry | Key expired before signing | Expired | Expired | 1 |
| B4-08 | Unverified manual claim says the key was revoked | Lifecycle event requires manual review | Active | Active | 1 |
| B4-09 | Credential references an unknown trust anchor | Trust anchor not established | Active (date-derived) | Active (date-derived) | 1 |
| B4-10 | Compromise event exists but signing timestamp is untrusted | Historical signing time not established | Compromised | Unknown | 2 |

The CSV result tracker in this directory records the expected and observed disposition IDs, fixture match, key states, finding counts, and scenario-specific notes.

## 3. Case-by-case interpretation

### B4-01 — Active key and current credential signature

The trust registry is shown as trusted, the key is active at assessment time and at signing, the signature result is supplied as valid, and the timestamp source is trusted under the fixture rules. No trust-anchor lifecycle findings were raised. This is the positive control.

The audit alteration checkbox was enabled in the supplied screenshot. It intentionally caused a separate audit-chain integrity warning and does not change the zero lifecycle-finding result.

### B4-02 — Old key rotated after credential signing

The key is currently rotated, but the trusted timestamp places the signature before the rotation effective time. The app retains a distinct historical pre-rotation state and advises retaining the historical verification record subject to issuer archival policy.

### B4-03 — Credential signed after routine key rotation

The trusted signing time follows the rotation effective time. The app returns that the old key had already been rotated and recommends verification using the replacement key recorded by the issuer.

### B4-04 — Key compromise effective before signature, reported later

The trusted compromise effective time precedes the credential's trusted signing time, while the report was recorded later. The app displays both the delayed-report chronology finding and the critical compromised-at-signing finding.

### B4-05 — Historical signature predates later key compromise

The trusted timestamp places signing before the compromise effective time. The current key state is compromised, while the historical state at signing is pre-compromise. The interface also surfaces the delayed-report chronology. This does not establish that the historical signature should be accepted; issuer archival policy and compromise investigation remain necessary.

### B4-06 — Expired key, signature timestamped before expiry

The key is currently expired, but the trusted signing time falls within its validity interval. The app distinguishes current expiry from historical signing state and raises no lifecycle finding under the fixture rules.

### B4-07 — Credential signed after key expiry

The trusted signing time is after the anchor expiry time. The app reports that the key expired before signing and recommends rejecting the signature and obtaining a current issuer-issued credential.

### B4-08 — Unverified manual claim says the key was revoked

The event is a manual claim with unverified authority/signature metadata. The app does not count it as a trusted lifecycle event and returns a manual-review disposition. This is not treated as confirmed revocation.

### B4-09 — Credential references an unknown trust anchor

The trust anchor is not registered and registry status is unknown. The app correctly returns Trust anchor not established. The screenshot also shows the date-derived lifecycle label as Active. These are separate concepts: date metadata can imply that a key is within its stated validity interval without establishing that the key belongs to a trusted issuer. A UI clarification has been added to make this distinction explicit.

### B4-10 — Compromise event exists but signing timestamp is untrusted

The client clock is not accepted as trusted time evidence. Although its supplied date appears earlier than the compromise effective time, the app returns Historical signing time not established and displays the historical key state as Unknown. The delayed-report chronology is separately surfaced.

## 4. Cross-case findings

1. **Current state and historical state are different questions.** Rotation and expiry after signing need not automatically erase the historical chronology, although archival policy determines reliance.
2. **Compromise chronology matters.** The effective time and recorded time must be retained separately.
3. **Trusted time is a prerequisite for historical ordering.** An untrusted client clock cannot establish whether signing preceded compromise.
4. **Registry trust is not the same as lifecycle status.** A key may appear within its date-based validity interval yet remain an untrusted or unknown anchor.
5. **Unauthenticated lifecycle assertions remain unverified.** A manual revocation claim does not become authoritative merely because it names a lifecycle event.
6. **Audit integrity is a separate dimension.** A tampered audit chain can coexist with an otherwise positive credential lifecycle assessment.

## 5. UI refinement

The B4-09 screenshot revealed a presentation ambiguity: displaying "Active" without a separate trust-registry status could be read as endorsement of an unknown key. The updated UI now explicitly separates:
- Trust registry status;
- Current key lifecycle state (metadata);
- Key lifecycle state at signing (metadata).

When anchor trust is not established, a warning explains that date-derived lifecycle state does not establish issuer trust or permit use of the key. When signing time is not trusted, the UI explicitly warns that historical ordering is unknown.

## 6. Audit-chain observation

The app demonstrates a session-generated hash-linked audit sequence. With the alteration control off, the displayed records verify. When the alteration control is enabled, a modified record is detected by hash recomputation. The hash-linked structure is not immutable storage: a party able to rewrite the entire log could recompute the chain unless an independent trusted checkpoint or protected external log is used.

## 7. Limitations

- All values and events are synthetic/manual fixture assertions.
- The application does not cryptographically verify credential signatures, timestamp tokens, key fingerprints, lifecycle-event signatures, or issuer directory responses.
- The app does not connect to a live trust registry, CRL, OCSP endpoint, timestamp authority, or university information system.
- The trust categories and source labels are assumptions in the research fixtures, not deployed trust anchors.
- Historical signature reliance depends on issuer policy, timestamp semantics, compromise scope, revocation reason, archival rules, and applicable law.
- The ten cases establish UI conformance to authored fixture rules, not real-world security accuracy or production readiness.

## 8. Conclusion

EACT-B4 completed all ten synthetic UI scenarios with the expected primary dispositions. The observed results support the prototype's ability to separate current key lifecycle state, historical state at signing, trusted-time availability, and trust-anchor registration assertions. The experiment also demonstrates detection of an altered audit record.

The most important next research step is to move from categorical scenario assertions to independently verifiable cryptographic evidence: actual public-key fingerprints, digital signatures, trusted timestamp tokens, signed lifecycle events, and governed trust-anchor distribution. Institutional integration must remain subject to university authorisation and privacy/security review.
