import json
from pathlib import Path

import pandas as pd
import streamlit as st

from eact_rules import evaluate_evidence, hash_only_baseline, evidence_completeness


st.title("Evidence-Aware Credential Triage Lab")
st.caption("EACT-v1 • Synthetic research scenarios • No external registry connection")

st.warning(
    "Research prototype only. All cases are fictional. This page does not verify "
    "real credentials, contact issuers, or make hiring decisions."
)

scenario_path = Path(__file__).resolve().parents[1] / "research" / "verification_scenarios.json"
with scenario_path.open("r", encoding="utf-8") as source:
    study = json.load(source)

scenarios = study["scenarios"]
scenario_by_title = {item["title"]: item for item in scenarios}

with st.sidebar:
    st.header("Scenario selection")
    selected_title = st.selectbox("Choose a fictional case", list(scenario_by_title))
    selected = scenario_by_title[selected_title]
    st.caption(selected["id"])
    st.divider()
    st.caption("Adjust evidence states to explore how the rules respond. Changes are temporary and do not edit the JSON fixture.")

    integrity_options = ["match", "mismatch", "not_checked"]
    issuer_options = ["authenticated", "unknown", "not_trusted"]
    status_options = ["active", "suspended", "revoked", "expired", "unknown"]
    subject_options = ["match", "mismatch", "not_checked"]
    source_options = [
        "available_consent_granted",
        "available",
        "status_source_available",
        "offline_document_only",
        "no_record_found",
        "service_unavailable",
        "status_service_unavailable",
        "consent_pending",
    ]

    def selected_index(options, value):
        return options.index(value) if value in options else 0

    integrity = st.selectbox("Document integrity", integrity_options, index=selected_index(integrity_options, selected["integrity"]))
    issuer = st.selectbox("Issuer identity", issuer_options, index=selected_index(issuer_options, selected["issuer_identity"]))
    credential_status = st.selectbox("Credential status", status_options, index=selected_index(status_options, selected["credential_status"]))
    subject = st.selectbox("Subject match", subject_options, index=selected_index(subject_options, selected["subject_match"]))
    source_state = st.selectbox("Source / consent state", source_options, index=selected_index(source_options, selected["source_state"]))

st.subheader(selected["id"] + " — " + selected["title"])
st.write(selected["risk_note"])

left, right = st.columns(2)
with left:
    st.markdown("#### Hash-only baseline")
    baseline = hash_only_baseline(integrity)
    st.metric("Shortcut output", baseline["label"])
    st.caption(baseline["warning"])

eact = evaluate_evidence(
    integrity=integrity,
    issuer_identity=issuer,
    credential_status=credential_status,
    subject_match=subject,
    source_state=source_state,
)

with right:
    st.markdown("#### Evidence-aware EACT output")
    st.metric("Disposition", eact["label"])
    st.caption(f"Evidence dimensions explicitly assessed: {evidence_completeness(integrity, issuer, credential_status, subject, source_state)} / 5")

st.info(eact["explanation"])
st.markdown("**Suggested next step**")
st.write(eact["next_action"])

st.divider()
st.subheader("All 10 predefined fictional scenarios")

rows = []
for item in scenarios:
    base = hash_only_baseline(item["integrity"])
    result = evaluate_evidence(
        integrity=item["integrity"],
        issuer_identity=item["issuer_identity"],
        credential_status=item["credential_status"],
        subject_match=item["subject_match"],
        source_state=item["source_state"],
    )
    rows.append({
        "ID": item["id"],
        "Scenario": item["title"],
        "Hash-only": base["label"],
        "EACT disposition": result["label"],
        "Matches predefined rule": result["disposition"] == item["expected_disposition"],
    })

table = pd.DataFrame(rows)
st.dataframe(table, use_container_width=True, hide_index=True)

conformant = int(table["Matches predefined rule"].sum())
st.caption(
    f"Rule-conformance check: {conformant}/{len(table)} fixtures match their "
    "predefined expected disposition. This is a software test against designed "
    "fixtures, not evidence of real-world accuracy."
)

with st.expander("Research interpretation and limitations"):
    st.markdown(
        "- A matching hash establishes a match to a reference digest, not issuer authenticity.\n"
        "- An unavailable source or pending consent produces an inconclusive/pending result, not a fraud label.\n"
        "- An authenticated issuer, active status, subject match, and integrity match are separate requirements.\n"
        "- The scenario set is designed for rule testing and is not a representative sample of actual hiring cases.\n"
        "- No real DigiLocker, NAD, university, or training-provider service is connected."
    )
