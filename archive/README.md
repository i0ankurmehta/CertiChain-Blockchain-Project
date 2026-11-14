# Legacy Archive

This folder preserves code and fixtures from the earlier CertiChain blockchain-ledger and EACT/VC prototype phases. The active Trust Gatekeeper research interface no longer imports these files.

## Preserved material

- `legacy_ledger_app_main.py`: the original remote `main` version of the blockchain-ledger Streamlit entrypoint.
- `legacy_ledger/data/synthetic_records.json`: old fictional ledger demo records.
- `legacy_eact_pages/`: five former Streamlit experiment pages, now removed from active navigation.
- `legacy_eact_modules/`: prior EACT rules, provenance, trust lifecycle, privacy and SD-JWT logic.
- `legacy_eact_tests/`: tests for those historical EACT modules.

The original `main` branch has not been changed by this research-branch migration.

The user's uploaded local `app.py` snapshot is not byte-identical to the remote `main` version. Preserve that local copy separately before pulling this branch; do not assume `legacy_ledger_app_main.py` contains local-only edits.

These modules and tests are retained for historical reproducibility. They are not part of the active Trust Gatekeeper runtime and should not be re-imported without a scope and dependency review.
