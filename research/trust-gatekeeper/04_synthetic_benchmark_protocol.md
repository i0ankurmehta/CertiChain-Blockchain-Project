# 04 — Synthetic Benchmark Protocol

**Version:** 0.1  
**Status:** Protocol specification; dataset not generated  
**Target size:** 240 synthetic cases

## 1. Objective

Create a reproducible controlled benchmark to test whether temporal graph reasoning, source-provenance handling and uncertainty-aware abstention improve preliminary academic-credential evidence triage over simpler baselines.

This benchmark measures system behaviour on constructed cases. It does not measure real-world fraud prevalence, the accuracy of real university registries, or performance on genuine candidate documents.

## 2. Dataset composition

Create **240 cases** across eight scenario families, with 30 cases per family.

Each family contains:
- 10 scan-only cases;
- 10 structured-only cases;
- 10 paired-input cases, in which a scan and structured record refer to the same claimed credential.

Total:
- 80 scan-only cases;
- 80 structured-only cases;
- 80 paired-input cases.

### Scenario families

| ID | Family | Controlled construction | Expected system behaviour |
|---|---|---|---|
| S1 | Valid historical status | Required synthetic institution/programme relationships cover the relevant study/award dates | Return evidence consistent, citing the time-bounded assertions |
| S2 | Changed recognition | Current status differs from status during the claimed period | Evaluate the historical period; do not apply current status retroactively |
| S3 | Programme or mode mismatch | Institution exists, but a programme or study mode is unsupported for the relevant session | Flag the specific unsupported relationship or abstain if evidence is ambiguous |
| S4 | Affiliation/campus change | College or campus relationship changes over time | Resolve the relationship for the candidate's dates, not from today's relationship |
| S5 | Rename, closure or merger | Institution identity/name changes and successor evidence is present or missing | Follow explicit identity evidence; abstain when continuity is unresolved |
| S6 | Conflicting sources | Two synthetic sources make incompatible claims about the same entity, predicate and period | Expose the conflict and supporting source details |
| S7 | Dependent sources | Multiple pages repeat or derive from one underlying source | Avoid counting copied claims as independent corroboration |
| S8 | Document/record mismatch | OCR-visible fields differ from structured record fields, or an injected visual anomaly is present | Report field mismatch and document anomaly separately |

The cases must contain fictional institutions, colleges, programmes, authorities, candidate names and source records. Use neutral synthetic logos or text-only document layouts. Do not reproduce real institutional seals, signatures, QR codes, letterheads or actual student data.

Every generated document must carry a visible **“SYNTHETIC — NOT A VALID ACADEMIC DOCUMENT”** watermark.

## 3. Input formats

- **Scanned document:** synthetic PDF or PNG/JPEG rendered from a clearly fictional template.
- **Structured record:** CSV or JSON.
- **Paired input:** both forms are supplied and the system must reconcile extracted and structured fields.

The benchmark should preserve input modality as an explicit dimension so that extraction errors are not confused with graph-reasoning errors.

For scan cases, store both:
- the ground-truth field values used to generate the image;
- the OCR-extracted values produced by the tested extraction system.

This permits separate measurement of extraction and evidence-reasoning stages.

## 4. Ground-truth label model

Do not label a synthetic case simply “fraudulent” or “genuine.” Use a multi-axis label.

### Primary expected evidence outcome
- `EVIDENCE_CONSISTENT`
- `TEMPORAL_MISMATCH`
- `ENTITY_AMBIGUITY`
- `SOURCE_CONFLICT`
- `EVIDENCE_INSUFFICIENT`
- `DOCUMENT_RECORD_MISMATCH`

### Independent flags
- `visual_anomaly_present`: boolean
- `source_dependency_present`: boolean
- `historical_change_present`: boolean
- `paired_input_present`: boolean
- `expected_abstention`: boolean

A case may have more than one independent flag, but one primary expected outcome should be assigned for the main metric. A secondary annotation may capture co-occurring issues.

Ground-truth labels describe the constructed evidence state—not whether a real candidate is dishonest or whether a qualification is legally valid.

## 5. Case schema

Minimum record:

```json
{
  "case_id": "TG-S2-004",
  "scenario_family": "S2_CHANGED_RECOGNITION",
  "input_mode": "paired",
  "credential_claim": {
    "institution_id": "SYN-INST-014",
    "college_id": "SYN-COL-008",
    "programme_id": "SYN-PROG-031",
    "qualification_id": "SYN-QUAL-006",
    "study_mode": "ODL",
    "admission_session": "2021-2022",
    "completion_date": "2024-06-30",
    "award_date": "2024-09-15"
  },
  "evidence_ids": ["SYN-EV-1001", "SYN-EV-1002"],
  "document_artifact_id": "SYN-DOC-004",
  "structured_record_id": "SYN-REC-004",
  "expected": {
    "primary_outcome": "TEMPORAL_MISMATCH",
    "expected_abstention": false,
    "visual_anomaly_present": false,
    "source_dependency_present": false
  },
  "template_group_id": "S2-TEMPLATE-B",
  "split": "test"
}
```

The values above are illustrative placeholders, not real institutions or regulatory facts.

## 6. Dataset construction and split

Use an explicit random seed and version the generator specification.

Recommended split:
- 60% development;
- 20% validation;
- 20% locked test.

Split by **template group and source-lineage family**, not by randomly scattering near-identical variants. Cases derived from the same scenario template, institution identity pattern or source family must not leak across development and test splits.

Keep each of the eight scenario families represented in all three splits where possible. Publish the split manifest and seed with the benchmark so results can be reproduced.

## 7. Baseline methods

Run all methods on the same locked cases:

| ID | Method | What it tests |
|---|---|---|
| B0 | Field/schema validation and exact matching | Basic data-quality baseline |
| B1 | Current-state institution/programme lookup | Whether a present-day result is incorrectly applied to historical cases |
| B2 | Static graph without time intervals | Value of entity relationships alone |
| B3 | Temporal graph | Added value of valid-time reasoning |
| B4 | Temporal graph + source provenance/dependency | Added value of lineage and conflict-aware evidence |
| B5 | B4 + uncertainty-aware abstention | Added value of declining to conclude on insufficient evidence |

Do not give B4 or B5 extra input information that the baselines do not receive, except information explicitly introduced by the method under test. Keep the underlying case evidence identical.

## 8. Metrics

### Classification and operational error
- Per-class precision, recall and F1.
- Confusion matrix.
- **False-clear rate:** proportion of cases with a known contradictory/unsupported condition that are incorrectly returned as evidence-consistent.
- **False-flag rate:** proportion of evidence-consistent cases incorrectly flagged with a mismatch or conflict.
- Abstention rate and coverage.

### Temporal reasoning
- Accuracy of the interval selected for each time-sensitive claim.
- Temporal false-clear rate on S2, S3 and S4.
- Correct handling of unknown or imprecise dates.

### Provenance
- Evidence-traceability coverage: proportion of findings linked to the source evidence used.
- Source-dependency detection precision/recall on S7.
- Dependent-source overcount rate: frequency with which copied sources are incorrectly treated as independent corroboration.
- Conflict identification and explanation completeness.

### Document extraction and reconciliation
- Field-level exact match / precision / recall for OCR-extracted fields.
- Document-to-record discrepancy detection rate.
- Separate reporting for OCR errors and actual injected content mismatches.

### Abstention
- Error rate among non-abstained cases.
- Risk-versus-coverage curve.
- Proportion of expected-abstain cases on which the system correctly abstains.
- Proportion of clear cases unnecessarily abstained on.

Do not report a single accuracy number without per-family results and error breakdowns.

## 9. Experimental procedure

1. Freeze the case generator, ontology, labels, split manifest and baseline definitions.
2. Generate development, validation and test cases using a fixed seed.
3. Validate ground truth independently from the code that performs the system assessment.
4. Run B0–B5 against identical case evidence.
5. Record outputs, source paths, timestamps, selected intervals and abstention decisions.
6. Evaluate metrics with a reproducible script.
7. Inspect every false-clear and false-flag case.
8. Publish the complete test manifest and limitations with the results.

Where possible, have a second reviewer inspect the labels and a sample of generated cases before the locked test is run.

## 10. Pre-registered comparisons

Primary comparisons:
- B1 versus B3 on time-dependent scenarios S2–S5.
- B2 versus B3 on historical relationship scenarios.
- B3 versus B4 on source-conflict and dependent-source scenarios S6–S7.
- B4 versus B5 on risk-versus-coverage and expected-abstain cases.

A positive result requires improvement on the targeted scenario family without concealing unacceptable regressions elsewhere. Do not declare success from a small improvement in aggregate accuracy if false-clear or false-flag errors worsen materially.

## 11. Reproducibility and artefacts

The later implementation should retain:
- generator version and random seed;
- synthetic institution/source registry;
- case manifest and ground-truth labels;
- document-generation templates;
- OCR outputs and extracted fields;
- source dependency graph;
- baseline configuration;
- experiment output JSON/CSV;
- metric script and environment lockfile.

No real candidate documents, personal identifiers or confidential BGV records belong in this benchmark.

## 12. Threats to validity

- Synthetic rules may be cleaner than real regulatory and institutional evidence.
- The source-dependency graph may be fully known in synthetic cases, while real-world lineage is often uncertain.
- Generated scans may not represent the quality and diversity of real certificates.
- The benchmark's label taxonomy reflects the designed ontology and may not match each BGV provider's operational policy.
- Results cannot establish real-world accuracy, candidate impact, customer demand, cost savings or compliance.
- A system can perform well on synthetic cases by learning generator patterns; holdout template groups and external review reduce but do not eliminate this risk.

## 13. Ethical and safety rules

- Use only fabricated candidate identities and institution names.
- Mark all generated documents as synthetic and invalid.
- Do not use real seals, signature specimens, QR codes or certificate layouts that could facilitate impersonation.
- Do not rank or blacklist real institutions.
- Do not produce a candidate fraud verdict.
- Keep “evidence insufficient” distinct from “not recognised” and “not authentic.”
