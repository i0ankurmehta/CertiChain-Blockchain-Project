# EACT Experiment B2 — Conflicting Evidence and Rule Precedence

**Purpose:** Examine how the current EACT first-match rules behave when multiple evidence dimensions point to different concerns.

## Research question

When credential evidence contains multiple simultaneous signals, does a single-label, first-match decision preserve enough information for a reviewer, or can it hide other relevant findings?

## Important distinction

The expected outputs below describe the current implementation's rule order. They are not ground truth, legal rules, or a claim that one signal should universally override another. The experiment is designed to reveal consequences of the current precedence choices.

## Procedure

1. Open the local Streamlit page **Evidence-Aware Credential Triage Lab**.
2. Select the scenario indicated.
3. Set all five evidence fields to the values in the table.
4. Record the EACT disposition, explanation, suggested next step, and the hash-only baseline.
5. Repeat for all seven cases.
6. Do not alter the source JSON fixture or commit any real personal data.

## B2 scenario matrix

| ID | Integrity | Issuer | Status | Subject | Source | Current expected output |
|---|---|---|---|---|---|---|
| B2-01 | mismatch | unknown | unknown | not_checked | service_unavailable | altered |
| B2-02 | match | authenticated | revoked | mismatch | status_source_available | revoked |
| B2-03 | match | unknown | revoked | mismatch | status_source_available | issuer_unverified |
| B2-04 | match | authenticated | active | mismatch | available | subject_mismatch |
| B2-05 | match | authenticated | unknown | match | status_service_unavailable | issuer_and_integrity_verified_status_unknown |
| B2-06 | mismatch | unknown | unknown | not_checked | consent_pending | altered |
| B2-07 | not_checked | unknown | unknown | not_checked | consent_pending | pending_consent |

## What to record

For every case capture:
- the disposition label;
- whether the explanation names all relevant evidence signals;
- whether any simultaneous concern is hidden by the first-match rule;
- whether the suggested next action is safe and useful;
- whether the hash-only baseline overstates certainty.

## Analysis questions

1. Which evidence dimension currently has the highest priority?
2. Which combinations produce a single label despite multiple adverse or incomplete signals?
3. Does the explanation distinguish a confirmed integrity mismatch from an unverified issuer?
4. Should the next EACT version return one primary disposition plus a list of all independent findings?
5. Which facts should be considered authoritative only when supplied by a trusted issuer/status source?

## Limits

This is a deterministic rule-behaviour experiment on synthetic inputs. It does not establish the best policy for real employers, the prevalence of conflicting evidence, or real-world verification accuracy. A policy preference would need stakeholder review and testing with authorised, appropriately de-identified cases.
