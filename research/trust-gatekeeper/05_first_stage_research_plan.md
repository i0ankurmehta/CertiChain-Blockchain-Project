# 05 — First-Stage Research Plan

**Version:** 0.1  
**Status:** Execution plan  
**Date:** 14 November 2026

## Objective

Decide whether the proposed temporal/provenance graph addresses a real BGV workflow problem and whether its added reasoning value can be demonstrated on a controlled benchmark—before changing the current CertiChain application.

## Workstream A — Competitor and workflow validation

### Tasks
1. Review the public product pages listed in the competitor matrix.
2. Arrange 5–8 exploratory conversations with education-verification analysts, BGV operations leads or product managers, if access is available.
3. Map their current case flow from candidate submission to final result.
4. Identify what is already automated and what is escalated to human review.
5. Ask for anonymised example problem categories, not candidate documents.
6. Request product demonstrations or technical descriptions from providers where possible.

### Required output
- A validated BGV workflow map.
- A feature-by-feature competitor matrix updated with demo/interview evidence.
- A list of operational pain points ranked by frequency and impact.
- A record of features that are already solved by existing vendor tools.

### Gate A — Customer/problem fit
Proceed only if practitioners identify a recurring problem involving historical status, affiliation/programme relationships, source conflicts, source traceability or evidence insufficiency. If they do not, revisit the product problem before implementation.

## Workstream B — Ontology review

### Tasks
1. Review the entity and relationship definitions with one domain-informed reviewer, if available.
2. Ensure recognition, accreditation, approval, affiliation and individual award verification are separate.
3. Confirm that the time model can represent academic sessions as well as exact dates.
4. Define what constitutes a source copy, derivative, conflict or independent source.
5. Identify which claims require human review.

### Required output
- Versioned ontology specification.
- Example graph records for each scenario family.
- Written rules for temporal applicability and abstention.

### Gate B — Model adequacy
Do not generate the final benchmark until each scenario family can be represented without inventing missing facts or collapsing distinct concepts.

## Workstream C — Synthetic benchmark

### Tasks
1. Implement a deterministic case generator in a research-only directory or standalone research project.
2. Generate 240 cases with scan-only, structured-only and paired-input modes.
3. Mark every synthetic document clearly and visibly.
4. Create labels independently from the assessment code.
5. Create template-group-aware development, validation and locked test splits.
6. Validate a sample of labels manually.

### Required output
- Dataset generator specification.
- Synthetic case manifest.
- Ground-truth label file.
- Benchmark data dictionary.
- Locked test split.

### Gate C — Benchmark quality
No model or graph result should be reported until the test cases are reproducible, the labels are auditable and template leakage has been checked.

## Workstream D — Baseline and proposed-method evaluation

### Tasks
1. Implement B0–B2 first.
2. Add time-bounded relationships for B3.
3. Add source lineage and dependency handling for B4.
4. Add an explicit abstention policy for B5.
5. Run all methods on the same cases.
6. Report family-level metrics and inspect false-clear/false-flag failures.

### Required output
- Reproducible baseline results.
- Ablation/comparison report.
- Error analysis.
- Threats-to-validity section.

### Gate D — Research contribution
Proceed with product/application integration only if B3/B4/B5 provide measurable value on their target cases compared with simpler alternatives, and do not achieve that value merely by using extra hidden information.

## Workstream E — Product and application decision

After Gates A–D:
- If customers recognise the problem and the method adds value, decide whether to develop an API/reviewer workflow.
- If customer pain exists but the graph adds no measurable value, simplify the product and do not force graph complexity.
- If the synthetic benchmark passes but customer evidence is weak, keep it as an academic prototype rather than claiming commercial readiness.
- If customer demand and research performance are both weak, stop or redefine the direction.

## Repository discipline

For the current phase:
- Research files live under `research/trust-gatekeeper/`.
- The existing Streamlit app, EACT pages and tests remain untouched.
- No new dependencies are added to the existing application's requirements.
- No application feature is implemented from the benchmark until the research gates are passed.

A separate repository should be created once this track has independent executable code, data-generation tooling or its own dependency/environment requirements. At that point the folder can be extracted cleanly and versioned independently.

## Immediate next action

Start with Workstream A: validate the analyst workflow and the assumed gap. The next code task should not be building the graph; it should be a deterministic synthetic case specification only after the problem and ontology pass review.
