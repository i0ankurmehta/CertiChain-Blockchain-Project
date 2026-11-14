# 10 — Evidence Adjudication and Decision Rules

**Document ID:** TG-RULES-001  
**Version:** 0.1  
**Date:** 14 November 2026  
**Status:** Proposed deterministic rules for the synthetic research prototype  
**Depends on:** TG-OPS-001, TG-OPS-002, TG-ONT-001 and TG-BENCH-001

> These rules govern preliminary evidence triage only. They do not establish legal recognition, authenticate an individual award, determine candidate intent, or make an employment decision.

---

## 1. Objective

Define a deterministic, testable method for converting a credential case and its evidence graph into:
- claim-specific findings;
- a case-level preliminary disposition;
- an explicit list of unresolved questions;
- a required human-review or external-verification action;
- a reproducible explanation linked to source evidence.

The engine must prefer a justified **unknown / insufficient / abstain** result over an unsupported positive or negative conclusion.

## 2. Core distinction: check scope versus case outcome

A case may contain several independent questions. Evaluate them separately rather than collapsing them into one universal trust score.

Required check scopes:
1. **Input consistency:** do the scan, OCR output and structured record agree?
2. **Entity resolution:** are the institution, college, campus, programme and awarding body identified?
3. **Institutional relationship:** was the relevant affiliation / constituent / campus relationship in force?
4. **Programme and mode status:** is there evidence for the exact programme and study mode in the relevant session?
5. **Individual award:** does the issuing authority's record confirm this candidate's award?
6. **Source quality and lineage:** what is each source competent to establish, and are sources independent, derived, conflicting or unknown?

A result for one scope must never be silently reused as a result for another. For example, an institution-level recognition assertion cannot satisfy the individual-award check.

## 3. Required output object

Every assessment returns a structured object with the following fields:

| Field | Required meaning |
|---|---|
| `case_id` | Stable case reference |
| `ruleset_id` | `TG-RULES-001` |
| `ruleset_version` | Version used for the assessment |
| `assessed_at` | Assessment timestamp |
| `case_state` | Received, blocked, in review, escalation pending or closed |
| `primary_outcome` | One of EV-01 through EV-07 |
| `secondary_findings` | Zero or more additional outcome codes |
| `scope_results` | Claim-specific outcomes for each applicable check |
| `evidence_ids` | All material evidence records used |
| `supporting_evidence_ids` | Evidence supporting each finding |
| `conflicting_evidence_ids` | Evidence that materially conflicts |
| `dependency_groups` | Sources grouped by known or suspected common lineage |
| `unresolved_questions` | Specific facts not established by supplied evidence |
| `recommended_action` | Human review, issuer confirmation, regulator clarification, correction request, or none |
| `explanation` | Plain-language reason, with time periods and source scope |
| `limitations` | What the assessment does not establish |
| `review_required` | Boolean plus reason |
| `review_status` | Pending, approved, returned, unresolved or not required |

Do not store a single unqualified scalar called `trust_score` as the authoritative output.

## 4. Outcome definitions

| Code | Meaning | Minimum trigger |
|---|---|---|
| EV-01 | Evidence consistent | All required contextual claims in the stated scope are supported and no material unresolved conflict, ambiguity or mismatch remains |
| EV-02 | Temporal mismatch | An in-scope source explicitly establishes a relevant status/relationship interval that does not cover the claimed relevant period, or explicitly excludes that period |
| EV-03 | Entity ambiguity | The identity of a material institution, college, campus, programme or awarding relationship cannot be resolved from adequate evidence |
| EV-04 | Source conflict | Two or more materially relevant, sufficiently comparable evidence claims make incompatible assertions and the conflict cannot be resolved deterministically |
| EV-05 | Evidence insufficient | A necessary claim lacks adequate, relevant, time-specific or claim-appropriate evidence, without enough evidence to establish an explicit contradiction |
| EV-06 | Document/record mismatch | Material fields extracted from a submitted artefact and a separate structured case record disagree after safe normalisation |
| EV-07 | Intake blocked | Processing authority is not documented, or an input fails safety / format / configured intake requirements |

EV-06 is an input-consistency finding; it can coexist with EV-02, EV-03, EV-04 or EV-05. EV-07 is a gate state: no substantive assessment should proceed while the blocking condition remains.

## 5. Decision precedence and coexistence

Do not force all findings into one code. The engine should return all material findings and a primary outcome for the case summary.

Apply the following primary-outcome precedence after the intake gate:

1. **EV-07 — Intake blocked:** terminal gate. Stop substantive processing.
2. **EV-04 — Source conflict:** use when comparable in-scope evidence makes incompatible claims and the conflict remains unresolved.
3. **EV-02 — Temporal mismatch:** use when valid-time evidence explicitly excludes the relevant claimed period.
4. **EV-03 — Entity ambiguity:** use when an essential entity or relationship cannot be resolved.
5. **EV-05 — Evidence insufficient:** use when the relevant entities are sufficiently resolved but evidence required for the scoped question is absent, undated, out of scope, non-authoritative for that claim, or otherwise insufficient.
6. **EV-06 — Document/record mismatch:** use as primary only when no higher-priority unresolved evidence finding exists; otherwise retain it as a secondary finding.
7. **EV-01 — Evidence consistent:** use only if the required scope checks pass and none of EV-02 through EV-07 applies.

This precedence is a deterministic summary convention, not a severity ranking about the candidate. A case may have multiple scope results. For example, an explicit programme-session mismatch may be EV-02 while individual-award verification remains EV-05.

## 6. Intake gate rules

### R-INT-01 — Authority required
If the customer has not documented the required purpose and applicable processing authority, return EV-07 and stop.

### R-INT-02 — Unsafe or unsupported file
If a file fails configured type, size, malware or parsing checks, quarantine/reject it and return EV-07 for the affected input.

### R-INT-03 — Synthetic-only research
In the current research phase, any real candidate document or identifiable candidate record is out of scope. Do not ingest it into the benchmark or test harness.

### R-INT-04 — Preserve source input
Never replace the original document/record with OCR, cleaned or normalised data. Derived values must retain their origin.

## 7. Field extraction and mismatch rules

### R-FLD-01 — Preserve raw and normalised values
For each field, store the original value, normalised comparison value, source input and extraction method.

### R-FLD-02 — Normalise only safe formatting differences
Permitted normalisation may include trimming outer whitespace, Unicode normalisation, case-folding for comparison and consistently formatting dates where the source is unambiguous. Do not erase meaningful spelling, script, transliteration, initials or date differences.

### R-FLD-03 — OCR uncertainty is not a mismatch
If OCR confidence is below a configured field-specific threshold, or the text is unreadable, mark the field uncertain and request review. Do not compare a low-confidence OCR string as if it were reliable.

### R-FLD-04 — EV-06
Return EV-06 when a material field differs between independent submitted representations after safe normalisation. Record both values and their origins.

### R-FLD-05 — No authenticity inference
Agreement between a scan and structured record does not prove either is authentic. A visual anomaly is recorded in a separate document finding and does not automatically cause EV-02, EV-03 or a fraud allegation.

## 8. Entity resolution rules

### R-ENT-01 — Exact identifiers first
Use a stable official identifier where available and appropriate. Store the identifier's issuing authority and scope.

### R-ENT-02 — Names are candidate matches
Exact or fuzzy name similarity alone does not prove entity identity. Fuzzy matching may generate candidates, but a human-reviewed alias or authoritative identity link is required for a conclusive resolution when the distinction is material.

### R-ENT-03 — Rename, merger and successor
Create explicit, time-bounded relationships such as RENAMED_TO or MERGED_INTO only when supported by an appropriate source. Do not merge historical nodes merely to simplify the graph.

### R-ENT-04 — EV-03
Return EV-03 when different plausible entities or relationships remain and the ambiguity changes the assessment.

### R-ENT-05 — Keep institutional concepts separate
Do not treat recognition, accreditation, approval, affiliation, campus permission, programme availability, awarding authority and individual award verification as synonyms.

## 9. Temporal reasoning rules

### R-TMP-01 — Identify the relevant event date
For each claim, state which event is being assessed: admission, programme delivery/study period, examination, completion or award. The applicable date depends on the rule and claim being evaluated.

### R-TMP-02 — Valid time versus observation time
Use valid_from / valid_to for when a status or relationship applied. Use published_at for when a source says it was published and observed_at for when the system captured it. Never substitute one for another.

### R-TMP-03 — Interval coverage
For exact-date claims, an assertion covers date D only when:
- valid_from is known and valid_from <= D; and
- valid_to is either known and D <= valid_to, or is explicitly open-ended under the source's stated semantics.

Boundary inclusivity must follow the source/authority's definition. The implementation must encode inclusive/exclusive bounds explicitly; do not assume all periods use the same boundary convention.

### R-TMP-04 — Session coverage
When the source and credential use academic sessions, compare session identifiers/intervals directly. Do not invent exact dates to force an interval comparison.

### R-TMP-05 — Explicit exclusion
If an in-scope source expressly says an approval does not apply retrospectively or excludes a specified session, and that excluded session is the candidate's relevant session, return EV-02 for that scope unless a separate applicable source resolves the issue.

### R-TMP-06 — Missing historical coverage is not contradiction
If no suitable source covers the historical period, return EV-05, not EV-02. Lack of evidence is not evidence of non-recognition.

### R-TMP-07 — Current status is not historical status
A current approved/recognised listing cannot, by itself, establish status in a prior session.

### R-TMP-08 — Unknown end date
A null valid_to means the end date is unknown unless the source expressly defines an open-ended period. Never silently interpret null as validity forever.

### R-TMP-09 — Date uncertainty
If the credential date/session or source effective period is too imprecise to determine overlap, return EV-05 or EV-03 as appropriate and abstain from a conclusive temporal finding.

### R-TMP-10 — Event-specific scope
Do not assume one date controls all questions. A programme approval may relate to admission session; an affiliation order may relate to a cohort or academic year; award register verification relates to the issuer's award record.

## 10. Evidence-source and provenance rules

### R-SRC-01 — Claim-specific competence
A source may support only claims within its documented authority and scope. For example, a recognition list does not verify a candidate's individual award.

### R-SRC-02 — Required provenance
Every material claim must link to its source, publisher, source type, capture time, publication/effective date if stated, content hash where retained, relevant excerpt and review state.

### R-SRC-03 — Source dependency groups
Where source B derives from source A, group them under the same lineage root. A chain A <- B <- C is one known evidence lineage, not three independent sources.

### R-SRC-04 — Unknown dependency
If dependency cannot be established, mark DEPENDENCY_UNKNOWN. Do not assume independence or dependence without evidence.

### R-SRC-05 — Dependency is not necessarily conflict
Repeated sources may be derivative and still accurately repeat the parent. This is a provenance limitation, not automatically EV-04.

### R-SRC-06 — Conflict comparability
Only classify two claims as a material conflict when they concern the same or resolvably identical subject, predicate, jurisdiction/scope and overlapping effective period, but assert incompatible values. Claims about different periods or different scopes are not conflicts merely because the wording differs.

### R-SRC-07 — Source conflict
If two comparable and claim-relevant sources make incompatible assertions and no documented rule resolves the conflict, return EV-04 and escalate.

### R-SRC-08 — Source priority
Do not implement arbitrary numerical authority weights in v0.1. Use explicit source classes and claim scope. If two sources of different classes conflict, explain their different scope and require review unless a governing official rule clearly resolves the question.

### R-SRC-09 — Not found semantics
Absence from a searched database means only that the item was not found in that database at the time and under the search method recorded. It does not prove invalidity.

## 11. Scope-specific adjudication

| Scope | EV-01 may mean | It does not mean |
|---|---|---|
| Input consistency | Submitted scan and structured record agree on checked fields | Document authenticity |
| Entity resolution | Entity/relationship is resolved for the stated purpose | Legal recognition or award validity |
| Institutional relationship | Required relationship is supported for relevant dates | Individual award exists |
| Programme/mode status | Appropriate evidence supports programme/mode for relevant session | Candidate completed/received award |
| Individual award | Issuer or authorised award record confirms the individual award | Every other credential claim is valid |
| Source lineage | Sources and dependencies are adequately represented | Sources are necessarily true |

A case summary may use EV-01 only with an explicit scope qualifier. If individual award verification is not performed or available, that scope must remain EV-05 or NOT_CHECKED; it must not inherit EV-01 from another scope.

## 12. Abstention and human review

The system must abstain from a conclusive finding when:
- a required source is missing, undated or outside scope;
- source dependency is unknown and independent corroboration is material;
- institution identity or successor relationship is unresolved;
- date precision prevents interval comparison;
- comparable authoritative sources conflict;
- OCR uncertainty affects a material field;
- required award-specific confirmation is unavailable.

Abstention is represented as EV-05 (evidence insufficient) or EV-03 (entity ambiguity), with review_required = true and a specific question/action. It is not a silent null result.

Mandatory second-person review:
- every EV-02, EV-03 or EV-04 in a real BGV workflow;
- every case with a potential adverse impact on a candidate;
- any proposed EV-01 used as a final customer outcome when issuer verification has not been separately completed;
- any case where the analyst overrides the system's primary outcome.

## 13. Deterministic evaluation sequence

The implementation should follow this order:

1. Validate processing authority and input safety. If blocked, return EV-07.
2. Preserve original inputs, hashes and receipt metadata.
3. Extract fields and record confidence/origin.
4. Reconcile scan, OCR and structured fields. Record EV-06 where material.
5. Resolve institution, college, campus, programme and awarding entities.
6. Build relevant claim-specific relationships and time intervals.
7. Group sources by known lineage and identify unknown dependency.
8. Check whether source claims are comparable and conflicting.
9. Evaluate temporal coverage for each applicable event/session.
10. Evaluate whether each required claim has evidence from a source competent to support it.
11. Produce scope-specific findings.
12. Apply the primary-outcome convention in Section 5.
13. Generate precise unresolved questions and recommended escalation.
14. Require human review where Section 12 applies.
15. Persist a reproducible output with ruleset version, evidence IDs and assessment timestamp.

## 14. Decision table for common edge cases

| Situation | Required result |
|---|---|
| Current listing says approved; no historical source for claimed session | EV-05, not EV-01 and not automatically EV-02 |
| Dated order explicitly excludes the claimed session | EV-02 for that programme/session scope |
| Two pages copy the same official order | One lineage group; no independent corroboration multiplier |
| Two sources disagree about different effective periods | Not a conflict unless their valid periods overlap and claims concern same scope |
| Two comparable in-scope sources disagree for same period | EV-04 and escalation |
| College name matches an institution, but no identity/affiliation evidence exists | EV-03 or EV-05 depending on whether identity itself is ambiguous or only evidence is missing |
| College affiliation is established, but candidate's individual award record is absent | EV-01 may apply to affiliation scope; EV-05 applies to award scope |
| Scan and JSON match, but issuer not contacted | Input-consistency EV-01; award-verification scope remains NOT_CHECKED / EV-05 |
| OCR reads a critical field with low confidence | Abstain on that field; human review |
| File fails security or format checks | EV-07; do not process |
| Source end date is null and semantics unknown | EV-05 if interval coverage depends on the end date |
| Name-only fuzzy match suggests a possible renamed institution | EV-03 until supported identity evidence is reviewed |

## 15. Required explanation format

Every non-EV-01 outcome must be explained in this sequence:

1. **Claim assessed:** the exact institutional/programme/award/document claim.
2. **Relevant period:** the date or academic session used.
3. **Evidence observed:** source IDs and the statements they support.
4. **Rule applied:** TG-RULES-001 rule identifier(s).
5. **Finding:** what is supported, contradicted, ambiguous or missing.
6. **Limitation:** what the finding does not establish.
7. **Next action:** a specific issuer/regulator/reviewer question or correction request.

Avoid generic explanations such as “risk high” or “AI detected an anomaly.”

## 16. Versioning and change control

- Every rule has a stable identifier.
- Rule changes require a version increment, written rationale and regression tests.
- A change to outcome precedence, temporal boundaries or source-class semantics is a major/minor ruleset change, not a silent patch.
- Every stored assessment records the ruleset version used.
- Old assessments are not silently reinterpreted when a new ruleset is deployed; they may be rerun with a new version and both outputs retained.
- The benchmark's expected labels must be reviewed separately from the implementation rules to avoid circular testing.

## 17. Minimum unit-test acceptance suite

The first Python implementation must include, at minimum:

1. missing processing authority -> EV-07;
2. unsafe/unsupported file -> EV-07;
3. exact scan/JSON agreement does not imply award verification;
4. material scan/JSON mismatch -> EV-06;
5. low-confidence OCR -> abstention/review;
6. valid historical interval -> contextual EV-01;
7. current-only status with no historical evidence -> EV-05;
8. explicit non-retroactive order excludes claimed session -> EV-02;
9. source and credential intervals that do not overlap -> EV-02 only when source scope explicitly covers/excludes the claim;
10. source interval/date precision unknown -> EV-05;
11. two derived directories share one lineage root;
12. unknown source dependency is not treated as independent;
13. same-scope overlapping contradictory assertions -> EV-04;
14. different time periods do not automatically produce EV-04;
15. affiliation evidence does not establish individual award;
16. unresolved successor identity -> EV-03;
17. null end date is not assumed to be open-ended;
18. EV-01 output carries explicit assessment scope and limitations;
19. primary and secondary outcomes follow the documented precedence;
20. every finding contains evidence IDs or an explicit missing-evidence explanation.

## 18. Non-goals

TG-RULES-001 does not define:
- legal equivalence or recognition decisions across countries;
- a universal regulatory authority ranking;
- a numerical fraud probability;
- automatic rejection or hiring decisions;
- an authenticity verdict from image forensics alone;
- a real-world source-crawling strategy;
- production retention periods or customer contract language.

**Status:** Ruleset v0.1 is ready for review and synthetic unit-test translation. It is not yet implemented or validated on real BGV cases.
