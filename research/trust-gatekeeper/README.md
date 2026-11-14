# CertiChain Trust Gatekeeper — Research Track

**Track status:** Foundation v0.1 — problem and benchmark design only  
**Date:** 14 November 2026  
**Market under study:** Indian background-verification (BGV) providers  
**Inputs:** Scanned academic documents and structured records  
**Data:** Synthetic only  
**Application status:** Existing Streamlit application is not modified by this track.

## Research proposition

Investigate whether a **temporal, provenance-aware evidence graph** can help BGV analysts assess difficult academic-credential cases more explainably and avoid unsupported conclusions.

This is not another credential repository, issuing service, blockchain ledger, or standalone fake-certificate detector. It is a proposed analyst-assist layer for cases where institution/programme relationships, recognition periods, affiliation history, source lineage, or submitted data are ambiguous or contradictory.

## Research pack

| Document | Purpose |
|---|---|
| [01 — Problem definition](01_problem_definition.md) | Frozen initial scope, user, problem, research questions and boundaries |
| [02 — Competitor and gap analysis](02_competitor_gap_analysis.md) | Publicly documented market capabilities and gaps that still need validation |
| [03 — Temporal provenance ontology](03_temporal_provenance_ontology.md) | Entities, relationships, temporal fields and evidence lineage |
| [04 — Synthetic benchmark protocol](04_synthetic_benchmark_protocol.md) | Dataset design, labels, baselines, metrics and validity safeguards |
| [05 — First-stage research plan](05_first_stage_research_plan.md) | Work sequence, gates and evidence required before application changes |
| [06 — Operational standards](06_operational_standards.md) | Case lifecycle, source classes, temporal checks, dispositions, escalation, privacy, security and release gates |

## Decision record

- Keep the current application and its main branch stable.
- Do not add another Streamlit lab or alter existing EACT modules during this foundation phase.
- Keep research documents isolated under `research/trust-gatekeeper/`.
- Revisit a separate GitHub repository once this track has an executable graph engine, benchmark generator, or independent dependency set. At that point, split this directory into a standalone repository rather than maintaining parallel codebases prematurely.

## Non-claims

The current work does **not** claim:
- that a synthetic benchmark establishes real-world fraud-detection accuracy;
- that CertiChain can authenticate an individual degree without the issuer;
- that public source absence proves a qualification is invalid;
- that current competitor products lack temporal or provenance capabilities;
- any quantified cost saving, turnaround improvement, or customer demand.

## Source discipline

Public vendor pages are treated as descriptions of vendor-claimed capabilities, not independent performance evidence. Official regulator and NAD pages are used for the specific rules and responsibilities they publish. Any interpretation or proposed technical distinction is labelled as a research hypothesis until tested.
