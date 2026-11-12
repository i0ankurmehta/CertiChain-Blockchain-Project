# Evidence-Aware Credential Triage Lab (EACT-v1)

This branch adds a research-only decision-support lab to CertiChain.

## New files
- `eact_rules.py`: deterministic, explainable evidence triage rules.
- `pages/1_Evidence_Triage_Lab.py`: Streamlit page comparing the hash-only shortcut with EACT.
- `tests/test_eact_rules.py`: unit tests against the 10 fictional scenario fixtures.

The page lets a user choose a scenario and temporarily modify the five evidence states to explore rule outcomes. It does not alter the blockchain ledger or the source JSON.

## Run
From the repository root:

```bash
python3 -m streamlit run app.py
```

Use Streamlit's page navigation to open **Evidence-Aware Credential Triage Lab**.

Run the deterministic tests:

```bash
python3 -m unittest discover -s tests -v
```

## Research caution
A 10/10 fixture conformance result means the implementation matches the expected outcomes defined by its own test specification. It is not a measure of real-world credential-verification accuracy, employer decision quality, fraud prevalence, or security. External issuer, status, subject, and consent evidence is simulated; no NAD or DigiLocker integration is included.
