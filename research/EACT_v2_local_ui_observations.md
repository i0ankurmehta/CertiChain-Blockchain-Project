# EACT-v2 Local UI Observations: Multi-Finding Conflict Tests

**Application:** CertiChain — Evidence-Aware Credential Triage Lab  
**Environment:** User-operated local Streamlit session  
**Screenshot date shown:** 13 November 2026  
**Evidence source:** Six user-supplied screenshots  
**Data:** Fictional/manual input combinations only

## 1. Revoked credential: effect of subject mismatch

Two captures show the same core input combination:
- Integrity: match
- Issuer: authenticated
- Credential status: revoked
- Source: available_consent_granted

The source value differs from the B2 protocol's token `status_source_available`. The current code recognises `available_consent_granted` as an available source value for the inactive-status finding. The screenshots are therefore recorded as a semantically accepted source-state variant, not an exact string-for-string replay of B2-02.

### Subject match variant
With Subject match set to `match`:
- EACT-v1 primary result: **Revoked**
- EACT-v2 primary disposition: **Revoked**
- EACT-v2 findings: **1 — Credential revoked**

### Subject mismatch variant
With Subject match set to `mismatch`:
- EACT-v1 primary result: **Revoked**
- EACT-v2 primary disposition: **Manual review — multiple adverse findings**
- EACT-v2 findings: **2 — Credential revoked; Subject mismatch**

**Observation:** EACT-v2 retains the revoked status but changes the primary disposition to manual review when a subject mismatch is also present. The findings table visibly preserves both signals. This demonstrates the intended multi-finding behaviour for this synthetic configuration.

## 2. Unknown issuer with a revoked-status claim

The captures show:
- Integrity: match
- Issuer identity: unknown
- Credential status: revoked
- Source: available or available_consent_granted
- Subject: match in one capture and mismatch in another

### Subject match variant
- EACT-v1 primary result: **Issuer unverified**
- EACT-v2 primary disposition: **Issuer unverified**
- EACT-v2 findings: **2 — Issuer not authenticated; Inactive status claim is not authenticated**

### Subject mismatch variant
- EACT-v1 primary result: **Issuer unverified**
- EACT-v2 primary disposition: **Issuer unverified**
- EACT-v2 findings: **3 — Issuer not authenticated; Inactive status claim is not authenticated; Subject mismatch**

**Observation:** EACT-v2 does not upgrade the revoked claim to an authenticated credential-status finding when the issuer is unknown. It still preserves the subject mismatch as a separate finding when supplied.

## 3. Integrity mismatch with other concerns

One screenshot shows:
- Integrity: mismatch
- Issuer identity: unknown
- Credential status: revoked
- Subject match: match
- Source: available

Observed outputs:
- Hash-only baseline: **INVALID (hash mismatch)**
- EACT-v1: **Altered — integrity mismatch**
- EACT-v2 primary: **Integrity check failed — document not intact**
- EACT-v2 findings: **3 — Integrity mismatch; Issuer not authenticated; Inactive status claim is not authenticated**

**Observation:** The integrity mismatch remains the primary disposition, while issuer uncertainty and the unauthenticated status claim are also visible. The UI explicitly notes that reference provenance is not independently represented.

## 4. Overall interpretation

The screenshot evidence supports these implementation-level observations:

1. A subject mismatch is not hidden when the supplied issuer and status evidence otherwise support a revoked finding; EACT-v2 exposes both and routes the combination to manual review.
2. An unknown issuer causes a revoked-status claim to remain unauthenticated; the status claim and subject mismatch can still be surfaced independently.
3. An integrity mismatch remains the primary disposition while other concerns remain visible in the findings table.
4. EACT-v2 adds explanatory detail without changing EACT-v1, which remains available as a comparison baseline.

## 5. UI improvement prompted by the screenshots

Several screenshots show the selected scenario title (for example EACT-01 or EACT-02) while the user has manually changed one or more evidence dropdowns. That can make an edited configuration appear to be the original fixture.

The lab UI is therefore being updated to:
- key dropdown state by scenario ID so switching scenarios loads that fixture's defaults;
- compare current controls with the selected fixture's original values;
- show an explicit warning when the current controls have been edited;
- provide an expandable view of the exact inputs used for the current result.

## 6. Limitations

- The screenshots show synthetic/manual assertions, not live issuer or registry responses.
- Source values in the B2-02/B2-03 examples are accepted available-source variants, not exact token matches to the protocol's `status_source_available`.
- These observations establish UI behaviour for the captured configurations only.
- They do not measure real-world credential verification accuracy, employer decision quality, or fraud prevalence.
- The app does not independently authenticate the source of a digest, issuer identity, credential status, or subject check.
