# CertiChain — Trust Gatekeeper

**Research branch:** `research/trust-gatekeeper-foundation`  
**Market under study:** Indian background-verification (BGV) providers  
**Research data:** Synthetic fixtures only  
**Current stage:** Deterministic rules engine and synthetic demonstration UI

## What this project does now

Trust Gatekeeper is an explainable analyst-assist research prototype. It evaluates scoped evidence claims about institutional relationships, programme status, historical periods, source conflicts and source lineage. It keeps individual award verification separate from institution/programme context.

It is **not** a degree-issuing platform, credential repository, blockchain ledger, automated candidate rejection system or proof of fraud.

## Run locally

```bash
python3 -m pip install -r requirements.txt
streamlit run app.py
```

The active interface uses only synthetic fixtures. Do not enter or upload real candidate, student or institutional personal data.

## Implemented in this branch

- `tg_rules.py` — deterministic TG-RULES-001 evidence adjudication engine.
- `tg_demo_cases.py` — fictional cases for historical programme approval, affiliation ambiguity and award-verification insufficiency.
- `tests/test_tg_rules.py` — 22 unit tests covering intake, temporal reasoning, source dependencies, conflicts, mismatches and award-verification boundaries.
- `research/trust-gatekeeper/` — problem definition, competitor gap, graph ontology, benchmark protocol, operational standards, analyst checklist, worked cases, adjudication rules and application audit.

## Current UI limitations

The Streamlit interface currently runs prebuilt synthetic cases and displays their findings. It does not yet implement actual PDF/image upload, OCR, CSV/JSON case intake, regulator-source ingestion, graph visualisation or issuer verification. These are later milestones and should be built only after the rule engine and benchmark are validated.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Expected current result: **22 tests pass**.

## Legacy experiments

The previous blockchain-ledger and EACT/VC experiments are preserved under [`archive/`](archive/README.md). Their old pages are removed from active navigation, and their backend modules/tests are archived. They are not imported into the active Trust Gatekeeper application.

The original `main` branch remains the legacy reference. The uploaded local `app.py` from the user's working copy differed slightly from remote `main`; preserve that local file separately before syncing this branch.
