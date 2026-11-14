# CertiChain — Trust Gatekeeper Research Branch

**Branch:** `research/trust-gatekeeper-foundation`  
**Research status:** Rules and workflow specification; synthetic-only stage  
**Market under study:** Indian background-verification (BGV) providers  
**Inputs under study:** Scanned academic documents and structured records  
**Current data:** Synthetic fixtures only

## What this branch is for

This branch isolates the new CertiChain research direction: an explainable, temporal and provenance-aware evidence triage system for difficult education-verification cases.

It is not intended to be another credential repository or blockchain ledger. The research asks whether representing institution/programme relationships with effective dates and source lineage can improve BGV analyst decisions and prevent unsupported conclusions.

## Important: application status

The root `app.py` on this branch is still the legacy academic credential-ledger demonstration inherited from the original project. It has not yet been replaced because the local working copy showed an uncommitted change to `app.py`; that work must be inspected and preserved before the entrypoint is simplified.

Therefore:
- Running `streamlit run app.py` still opens the legacy ledger demo, **not** the new Trust Gatekeeper.
- The five older EACT Streamlit pages have been removed from active navigation on this branch and preserved under `archive/legacy_eact_pages/`.
- Their backend modules, tests and experiment records remain as historical research.
- Do not treat the legacy ledger, proof-of-work, simulated tampering or SD-JWT experiments as active Trust Gatekeeper features.
- The original `main` branch has not been changed.

## Research documents

The complete research pack is in [`research/trust-gatekeeper/`](research/trust-gatekeeper/README.md).

Key documents:
1. Problem definition
2. Competitor and gap analysis
3. Temporal provenance ontology
4. Synthetic benchmark protocol
5. First-stage research plan
6. Operational standards
7. Analyst case-handling checklist
8. Worked affiliation-transition case
9. Worked temporal-approval/source-dependency case
10. Evidence adjudication and decision rules
11. Legacy application feature audit and retirement plan

## Current implementation boundary

No production credential checks, real candidate personal data, live registry scraping, automatic adverse decisions or real-world accuracy claims are permitted in this research phase.

The next implementation step is to translate `TG-RULES-001` into an independent deterministic Python module and tests, then evaluate it against the synthetic cases before creating the new Trust Gatekeeper UI.

## Local setup

The research branch can be checked out with:

```bash
git fetch origin
git switch --track origin/research/trust-gatekeeper-foundation
```

When already on this branch, update with:

```bash
git pull --ff-only
```

Check `git status --short` before any destructive cleanup. Preserve any local modifications to `app.py`.
