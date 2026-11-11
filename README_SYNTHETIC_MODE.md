# Synthetic Ledger Mode

The application includes two separate Streamlit session-state ledgers:

- `manual_chain` — the normal user-entered ledger.
- `synthetic_chain` — a demonstration ledger built from `data/synthetic_records.json`.

Use the **Turn on Synthetic Data Records** toggle in the sidebar to display the synthetic ledger. Turning it off returns to the manual ledger; it does not merge, reset, or overwrite manual records.

The synthetic ledger includes its own genesis block and one mined block per fictional record. Tampering and reset actions affect only the currently active ledger.

All included names and academic details are fictional. No university data is connected.
