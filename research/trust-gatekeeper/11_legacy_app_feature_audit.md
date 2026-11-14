# 11 — Legacy Application Feature Audit and Retirement Plan

**Document ID:** TG-APP-001  
**Version:** 0.1  
**Date:** 14 November 2026  
**Scope:** Current `main` branch application inspected on 14 November 2026; this document proposes the future active product scope for the Trust Gatekeeper research branch.

## 1. Why an audit is necessary

The existing application was built as a blockchain academic-credential ledger and then expanded with EACT research labs around evidence triage, provenance freshness, trust-anchor lifecycle, privacy-preserving disclosure and SD-JWT selective disclosure.

The selected direction is now different: an India-first analyst-assist workflow for BGV teams, based on scanned and structured inputs, temporal institutional/programme relationships, source provenance, explainable findings and human escalation.

The old experiments should remain reproducible as project history, but they should not all remain in the active product interface. Keeping every experiment visible as a feature makes the product harder to understand and implies that unrelated VC/cryptographic functions are part of the BGV value proposition.

## 2. Current application inventory (remote main branch)

Inspection performed against GitHub `main` on 14 November 2026. The local working copy shown earlier had an uncommitted modification to `app.py`; that local file was not available for inspection.

### Main screen — `app.py`

Publicly visible functions in the inspected version:
- manual credential record entry (student name, roll number, course, CGPA);
- repository synthetic record mode;
- CSV/JSON upload;
- approved online JSON endpoint fetch (allowlisted host);
- independent local hash-chain construction and proof-of-work mining;
- ledger display/explorer;
- tampering simulation and ledger rebuild/reset controls;
- imported-record session reset/rebuild controls.

### Multipage EACT UI

| Page | Existing purpose | Future product relevance |
|---|---|---|
| `pages/1_Evidence_Triage_Lab.py` | EACT-v1/v2 fictional scenario triage with integrity, issuer, credential-status, subject and source/consent inputs | Historical research only; its outcome taxonomy is not TG-RULES-001 |
| `pages/2_Provenance_Freshness_Lab.py` | Source/issuer/status freshness, age and timestamp checks | Retain selected provenance ideas; archive the UI and replace age heuristics with valid-time + observed-time semantics |
| `pages/3_Trust_Anchor_Lifecycle_Lab.py` | Trust-anchor registration, key/signature/timestamp and lifecycle-event checks; audit hash-chain demonstration | Not part of BGV v1; archive the UI and preserve as separate cryptographic research |
| `pages/4_Privacy_Preserving_Credential_Lab.py` | Verifier purpose, disclosure request, retention, issuer-trust and credential disclosure assessment | Keep privacy/data-minimisation principles in operational standards; archive this as a separate disclosure experiment |
| `pages/5_Cryptographic_Selective_Disclosure_Lab.py` | SD-JWT issuer, holder presentation, verifier binding and online credential intake | Not needed for the BGV evidence-graph MVP; archive as a separate credential-format experiment |

### Backend modules and tests

- `eact_rules.py`: existing EACT triage rules.
- `eact_provenance.py`: freshness/provenance assessment rules.
- `eact_trust_lifecycle.py`: trust-anchor lifecycle and audit trail.
- `eact_privacy.py`: disclosure evaluation.
- `eact_sdjwt.py`: selective-disclosure credential functions.
- `tests/test_eact_*.py`: regression tests for those experiments.

These modules and tests have been copied byte-for-byte into `archive/legacy_eact_modules/` and `archive/legacy_eact_tests/` on the research branch, then removed from the active import/test paths. Their source and test history remains available. Do not import them into the new TG engine without an explicit design review.

## 3. Feature disposition

| Existing feature | Decision | Reason | Replacement / reuse |
|---|---|---|---|
| Proof-of-work mining for every academic record | **Retire from active Trust Gatekeeper product** | Does not establish issuer truth, programme status or source authority; adds compute and UI complexity | Preserve provenance/content hashes for source artefacts and assessment versions where useful |
| Blockchain block explorer | **Retire from active product** | BGV analyst needs a case evidence trail, not a student credential chain | Case timeline and source-linked finding history |
| Simulated ledger tampering controls | **Remove from active workflow** | Developer demonstration, not a BGV analyst task; can imply a false security guarantee | Keep only in legacy demo/history if needed |
| Manual student/CGPA issuance form | **Retire from BGV workflow** | New product is not an issuing authority and should not create awards | Synthetic case fixture creation and analyst-controlled annotations |
| Repository synthetic records | **Keep only as research fixture source** | Useful for controlled tests, not a customer-facing operating mode | Versioned synthetic benchmark case loader |
| CSV/JSON upload | **Retain concept, redesign schema** | Structured intake is in the selected scope | Credential case intake schema, validation and provenance |
| Allowlisted online JSON endpoint | **Disable for MVP pending source-governance design** | Allowlisting a host alone does not establish source competence, scope, date validity, data permissions or authenticity | Curated source records with explicit publisher, claim scope, effective dates, capture dates and review |
| Imported-session clear/rebuild buttons | **Remove from analyst UI** | Session debugging controls, not normal case handling | Controlled case lifecycle and authorised correction/reset workflow |
| Evidence Triage EACT-v1/v2 page | **Archive UI** | It has a different EACT taxonomy and user interaction model | Translate only reviewed concepts into TG-RULES-001 |
| Provenance Freshness page | **Archive UI; reuse concepts selectively** | Freshness age is not the same as historical validity or source lineage | Temporal + provenance model in TG ontology and rules |
| Trust Anchor Lifecycle page | **Archive UI** | BGV scope does not currently need credential key lifecycle management | Keep as separate historical cryptographic experiment |
| Privacy Disclosure page | **Archive UI; retain privacy safeguards** | User-facing disclosure selection is not the first BGV problem | Keep purpose limitation/data minimisation in TG operational controls |
| SD-JWT page and online credential fetch | **Archive UI; exclude from BGV v1** | Adds issuer/holder/wallet/cryptographic flow unrelated to selected first buyer workflow | Revisit only if an actual BGV customer requires VC/SD-JWT ingestion |
| EACT backend modules and tests | **Retain in repository history; do not delete now** | Preserve experiments, tests and traceability | New TG rules engine gets its own module/tests after rule review |

## 4. Proposed future active Trust Gatekeeper UI

Keep the first operational interface to five primary areas:

1. **Case intake** — create a case, record purpose/authority confirmation and upload a scan and/or structured record.
2. **Claim extraction** — show original and extracted values side by side with field-level uncertainty.
3. **Evidence graph / timeline** — show institutions, college affiliation, campus/programme relationships, effective intervals and source lineage.
4. **Assessment** — show claim-specific EV outcomes, supporting/conflicting evidence and abstention.
5. **Review and export** — analyst explanation, targeted escalation question, second-person review and an auditable evidence report.

Do not add dashboards, blockchain, wallets, token issuance, public directories, automatic candidate scoring, bulk web scraping or multiple independent labs until a validated BGV workflow requires them.

## 5. Safe cleanup sequencing

The following must happen in order:

### Phase A — Preserve and baseline
- Keep current `main` unchanged as the legacy reference.
- Keep `research/trust-gatekeeper-foundation` separate.
- Record the current remote baseline commit and existing tests.
- Preserve the user's local uncommitted `app.py` edit; do not overwrite or reset it.
- Archive existing EACT docs/modules/tests in Git history.

### Phase B — Rules first
- Review and freeze TG-RULES-001.
- Translate its rules into a new independent `tg_rules.py` module and tests.
- Do not import existing EACT modules merely because names sound similar.

### Phase C — Retire old active UI
- [x] Move the five EACT pages out of active Streamlit navigation into `archive/legacy_eact_pages/`.
- [x] Preserve the original remote `main` ledger entrypoint at `archive/legacy_ledger_app_main.py`.
- [x] Replace the research branch root `app.py` with the minimal Trust Gatekeeper synthetic-case interface.
- [x] Archive the EACT backend modules and regression tests outside the active import/test paths.
- [x] Archive the former ledger synthetic-record fixture.
- [x] Reduce active `requirements.txt` to Streamlit only after archiving the unused JWT/requests-dependent modules.
- [ ] Preserve the user's uploaded local-only `app.py` edits separately before syncing; the upload is not byte-identical to remote `main`.

### Phase D — Minimal vertical slice
Build only one end-to-end synthetic case:
- scan/structured intake;
- extraction and reconciliation;
- temporal/provenance evidence record;
- deterministic TG-RULES-001 assessment;
- evidence report and audit trail.

Do not add live source fetching, production candidate data, cryptographic wallets or blockchain mechanics in this slice.

## 6. Cleanup actions performed and local working-copy safeguard

### Completed on the research branch
- All five legacy EACT Streamlit page files were copied to `archive/legacy_eact_pages/` and removed from active navigation.
- The five EACT backend modules were copied to `archive/legacy_eact_modules/` and removed from the active import path.
- The five EACT regression tests were copied to `archive/legacy_eact_tests/`; `tests/` now contains the new Trust Gatekeeper rules tests.
- The old synthetic ledger dataset was preserved at `archive/legacy_ledger/data/synthetic_records.json`.
- The original remote `main` ledger entrypoint was preserved at `archive/legacy_ledger_app_main.py`.
- The research branch root `app.py` is now the Trust Gatekeeper synthetic-case interface.
- `requirements.txt` now lists only Streamlit for the active app.
- The original `main` branch was not changed.

### Local-only uploaded app safeguard

The user uploaded a local `app.py` snapshot for this transition. It is 25,095 bytes / 599 lines and is not byte-identical to the remote `main` app; the remote `main` version was archived separately. The uploaded local snapshot remains in the conversation attachment and the user's working copy. Before syncing, the user must create a separate local backup and stash the working changes. Do not pop the stash over the new Trust Gatekeeper `app.py` without reviewing it.

## 7. Cleanup acceptance criteria

The cleanup is complete only when:
- no legacy EACT lab appears in the active Trust Gatekeeper navigation;
- no proof-of-work miner or tampering simulation appears in the Trust Gatekeeper analyst workflow;
- no manual credential-issuance form appears;
- the new UI has only the five primary areas in Section 4;
- old EACT research remains accessible in an archive/history location;
- imports and dependencies are minimised without breaking the new tests;
- the synthetic end-to-end case passes the TG-RULES-001 tests;
- the original legacy `main` remains recoverable.

**Decision:** retain the legacy app as historical reference on `main`, and make the research branch the clean future Trust Gatekeeper product direction. Do not mix both sets of concepts in the active analyst workflow.
