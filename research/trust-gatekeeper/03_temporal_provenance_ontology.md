# 03 — Temporal Provenance Graph Ontology

**Version:** 0.1  
**Status:** Conceptual schema; not yet implemented

## 1. Design principles

1. **A claim is not a fact merely because it appears in a source.** Store the claim and the evidence supporting it separately.
2. **Names are not identities.** Institutions may change names, merge, close or have successor bodies.
3. **Status is time-bounded.** Current status must not be retroactively applied to every past credential.
4. **Source count is not source independence.** Several pages may derive from one notice.
5. **Unknown is a valid state.** Missing or ambiguous evidence must not be converted into a negative legal conclusion.
6. **Issuer verification is separate.** The graph may assess contextual evidence; it does not independently prove that an individual award exists in the issuer's records.

## 2. Core node types

| Node type | Purpose | Important attributes |
|---|---|---|
| `CredentialCase` | One synthetic BGV case | `case_id`, `created_at`, `input_mode`, `expected_label` |
| `CredentialClaim` | Candidate-stated qualification | `claim_id`, `qualification_title`, `award_date`, `admission_date`, `completion_date`, `study_mode` |
| `DocumentArtifact` | Scanned certificate or marksheet | `artifact_id`, `mime_type`, `content_hash`, `synthetic_marker`, `received_at` |
| `StructuredRecord` | CSV/JSON case record | `record_id`, `schema_version`, `content_hash`, `received_at` |
| `Institution` | Legal/recognised higher-education entity | `institution_id`, `canonical_name`, `entity_type`, `jurisdiction` |
| `InstitutionAlias` | Historical or alternate name | `alias_id`, `name`, `language`, `valid_from`, `valid_to` |
| `Campus` | Campus or approved location | `campus_id`, `name`, `location`, `valid_from`, `valid_to` |
| `College` | Affiliated or constituent college | `college_id`, `name`, `entity_type` |
| `Programme` | Programme or course | `programme_id`, `title`, `level`, `discipline`, `mode` |
| `Qualification` | Award type/degree specification | `qualification_id`, `title`, `level`, `specification` |
| `Authority` | Regulator, statutory council or awarding authority | `authority_id`, `name`, `authority_type`, `jurisdiction` |
| `StatusAssertion` | A time-bounded recognition/approval/affiliation claim | `assertion_id`, `status_type`, `status_value`, `valid_from`, `valid_to` |
| `SourceDocument` | Notice, order, web page, record or official circular | `source_id`, `source_uri`, `source_type`, `publisher`, `published_at`, `captured_at`, `content_hash` |
| `EvidenceClaim` | Atomic statement extracted or entered from a source | `evidence_id`, `subject_id`, `predicate`, `object_id/value`, `extraction_method`, `review_state` |

For the initial synthetic benchmark, regulator and institution sources are generated fictional source records. No real candidate or university data is ingested.

## 3. Core relationship types

| Relationship | Direction | Meaning |
|---|---|---|
| `AWARDED_BY` | CredentialClaim → Institution | Claimed awarding institution |
| `CLAIMED_FOR` | CredentialClaim → Programme | Claimed programme |
| `CLAIMED_QUALIFICATION` | CredentialClaim → Qualification | Claimed award |
| `ISSUED_AS_DOCUMENT` | CredentialClaim → DocumentArtifact | Document supporting the claim |
| `HAS_STRUCTURED_RECORD` | CredentialCase → StructuredRecord | Structured input for the case |
| `AFFILIATED_WITH` | College → Institution | College affiliation during a specified period |
| `CONSTITUENT_OF` | College → Institution | Constituent-college relationship during a specified period |
| `OPERATES_CAMPUS` | Institution → Campus | Institution/campus relationship |
| `OFFERS_PROGRAMME` | Institution or College → Programme | Programme-offering relationship |
| `AWARDING_AUTHORITY_FOR` | Institution → Qualification/Programme | Authority to award the relevant qualification, where evidenced |
| `APPROVED_BY` | Programme/Institution/Campus → Authority | Approval or recognition assertion |
| `ACCREDITED_BY` | Institution/Programme → Authority | Accreditation assertion; distinct from recognition/approval |
| `RENAMED_TO` | Institution → InstitutionAlias or successor entity | Identity/name continuity assertion |
| `MERGED_INTO` | Institution → Institution | Merger or successor relationship |
| `SUPPORTED_BY` | EvidenceClaim/StatusAssertion → SourceDocument | Evidence source supporting the claim |
| `DERIVED_FROM` | SourceDocument/EvidenceClaim → SourceDocument/EvidenceClaim | Provenance dependency |
| `CONTRADICTS` | EvidenceClaim ↔ EvidenceClaim | Explicit conflict relation |
| `RELATES_TO_CASE` | EvidenceClaim → CredentialCase | Evidence relevance to a case |

Each relationship that can change over time must carry its own time interval; do not assume that the connected entities' existence implies the relationship was valid for all dates.

## 4. Temporal model

Use two primary time dimensions, plus source publication time.

| Field | Definition |
|---|---|
| `valid_from` | Earliest date on which the claim/relationship applied in the real world |
| `valid_to` | Last date on which it applied; null means no known end, not proof of indefinite validity |
| `observed_at` | When the research system collected or recorded the evidence |
| `published_at` | When the source says it was published, if known |
| `recorded_at` | When the assertion was entered into the graph |
| `date_precision` | Exact day, month, year, session, or unknown |
| `timezone` | Timezone where the timestamp has a local-time meaning |

**Valid time** answers: “When did this status or relationship apply?”  
**Observation/transaction time** answers: “When did our system know or record this evidence?”

Do not invent a precise date where the source only provides an academic session or year. Preserve the precision and original wording.

Example: a synthetic approval assertion can have `valid_from = 2021-07-01`, `valid_to = 2022-06-30`, `published_at = 2021-08-15`, and `observed_at = 2026-11-14`. The publication date is not the effective date.

## 5. Provenance model

Every evidence assertion should retain:
- source identifier and URI (synthetic URI in the benchmark);
- source publisher and source type;
- source content hash and capture timestamp;
- the exact passage/structured field supporting the claim;
- extraction method (manual, structured import, OCR or other parser);
- review state (unreviewed, human-reviewed, rejected);
- the source from which this source was copied or derived, when known;
- any contradictory evidence assertion.

Do not assign arbitrary numerical authority weights in v0.1. Preserve categorical source metadata and test transparent rules first. Any later source-ranking method must be justified and evaluated separately.

## 6. Identity resolution

Use stable synthetic IDs and explicit alias/successor edges. Do not merge two institutions solely because their names are similar.

Minimum identity evidence for a synthetic identity link should include one or more of:
- explicit legal name-change relation;
- official merger/successor statement represented as a source claim;
- explicit institutional identifier in the synthetic record;
- human-reviewed identity assertion.

If identity cannot be resolved, retain `Entity ambiguity` rather than silently selecting the closest name match.

## 7. Evidence dependency

Represent source lineage as a directed acyclic graph where possible:
- `Source A` may be the original official notice.
- `Source B` may reproduce the notice.
- `Source C` may quote Source B.
- B and C should not count as two independent confirmations of A's underlying assertion.

Use `DERIVED_FROM` when the dependency is known. Use `DEPENDENCY_UNKNOWN` or an explicit unknown state when it cannot be established. Do not infer that two sources are independent merely because their URLs differ.

## 8. Case-resolution semantics

For a credential case, evaluate:
1. which entities are claimed;
2. which relationships are needed for the claimed qualification and study mode;
3. which dates are relevant (admission, study period, completion, award);
4. which assertions cover those dates;
5. which source documents support each assertion;
6. whether sources conflict or are dependent;
7. whether enough evidence exists to return a conclusive preliminary assessment.

The graph does not decide legal equivalence or authenticate the individual's transcript/degree. It returns explainable evidence findings and a next-step recommendation.

## 9. Minimal example (illustrative only)

```text
CredentialCase C-001
  └── CredentialClaim Q-001
       ├── AWARDED_BY → Institution I-10
       ├── CLAIMED_FOR → Programme P-21
       └── ISSUED_AS_DOCUMENT → Document D-001

Institution I-10
  └── OFFERS_PROGRAMME → Programme P-21
       └── APPROVED_BY → Authority A-UGC
            └── StatusAssertion S-2021
                 └── SUPPORTED_BY → SourceDocument SRC-01

SourceDocument SRC-02
  └── DERIVED_FROM → SourceDocument SRC-01
```

The example does not assert any real university status. It shows that a case should be traceable from a claim to a status assertion and then to the source evidence.

## 10. Ontology invariants

- Every status assertion has a source or is explicitly labelled as a synthetic fixture.
- Every time-bounded relationship records its temporal precision.
- A null end date means “end date not known,” not “valid forever.”
- A source's publication date is never substituted for its effective date.
- Institution recognition is not treated as individual award authentication.
- Accreditation, recognition, approval, affiliation and awarding authority remain distinct predicates.
- Unknown, insufficient and conflicting evidence are first-class states.
- A copied source is not counted as independent corroboration of its parent.
