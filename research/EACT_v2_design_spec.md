# EACT-v2 Design Specification — Multi-Finding Assessment

## Motivation

The EACT-B2 synthetic conflict experiment showed that EACT-v1's first-match rule returns one primary label while hiding other simultaneous inputs. Examples:
- A revoked credential plus subject mismatch returns only Revoked.
- An unknown issuer plus a revoked-status claim and subject mismatch returns only Issuer unverified.
- An integrity mismatch plus a source outage returns only Altered.

The next design iteration retains the EACT-v1 baseline and introduces EACT-v2 as a separate output.

## Proposed output

EACT-v2 returns:
1. One primary disposition for quick triage.
2. A list of all detected findings across the five evidence dimensions.
3. Severity labels for interface prioritisation.
4. The supplied value and dimension for each finding.
5. An authority/provenance caveat for each finding.
6. A suggested next action for each finding and for the overall disposition.

## Evidence handling rules

- An integrity mismatch is reported as a mismatch, but the lab must disclose that reference provenance is not independently represented.
- An issuer that is unknown or not trusted is reported as not authenticated.
- Revoked/suspended/expired status is treated as an authenticated status only where the scenario says the issuer is authenticated and the source is available. Otherwise it is shown as an unauthenticated status claim.
- Subject mismatch is retained as a finding; the lab does not perform identity proofing.
- Consent pending, no record returned, and source unavailable remain workflow/evidence availability findings, not fraud classifications.
- The output must state that all inputs are synthetic/manual and not independently fetched or authenticated.

## Primary-disposition policy in this prototype

The following ordering is a transparent prototype policy, not an established universal standard:
1. Integrity mismatch -> integrity failure.
2. Consent pending -> pending consent.
3. No record returned -> inconclusive/manual review.
4. Source unavailable -> partial verification only for the narrow authenticated-issuer + matching-integrity + matching-subject + unknown-status case; otherwise inconclusive.
5. Issuer not authenticated -> issuer unverified.
6. Authenticated inactive status plus subject mismatch -> manual review with multiple findings.
7. Authenticated inactive status -> revoked/suspended/expired.
8. Subject mismatch -> subject mismatch.
9. Missing integrity/subject/status evidence -> incomplete.
10. All required positive conditions -> verified against trusted source.

A primary label never suppresses the independent findings list.

## Evaluation plan

Re-run all seven B2 conflict cases and the ten EACT-v1 base fixtures. Focus on:
- whether every simultaneous signal appears in findings;
- whether status claims are appropriately caveated when issuer identity is unknown;
- whether source unavailability and pending consent remain non-fraud states;
- whether EACT-v1 and EACT-v2 primary dispositions differ only where the new policy explicitly calls for it;
- whether the unit tests pass.

## Scope limits

EACT-v2 is an explainable deterministic rules prototype. It is not an AI model, legal decision engine, issuer authentication service, or production credential verifier. Finding provenance is currently a declared limitation; no source signatures, issuer registry responses, status lists, or identity proofing are connected.
