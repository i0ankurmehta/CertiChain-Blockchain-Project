import json
from pathlib import Path

import pandas as pd
import streamlit as st

from eact_rules import (
    evaluate_evidence,
    evaluate_evidence_v2,
    hash_only_baseline,
    evidence_completeness,
)


st.title("Evidence-Aware Credential Triage Lab")
st.caption("EACT-v2 preview • Multi-finding output • Synthetic research scenarios")

st.warning(
    "Research prototype only. All cases are fictional. This page does not verify "
    "real credentials, contact issuers, or make hiring decisions."
)

root = Path(__file__).resolve().parents[1]
scenario_path = root / "research" / "verification_scenarios.json"
b2_path = root / "research" / "EACT_B2_conflict_scenarios.json"

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

inputs = {
    "integrity": integrity,
    "issuer_identity": issuer,
    "credential_status": credential_status,
    "subject_match": subject,
    "source_state": source_state,
}

st.subheader(selected["id"] + " — " + selected["title"])
st.write(selected["risk_note"])

v1 = evaluate_evidence(**inputs)
v2 = evaluate_evidence_v2(**inputs)
baseline = hash_only_baseline(integrity)

left, right = st.columns(2)
with left:
    st.markdown("#### Hash-only baseline")
    st.metric("Shortcut output", baseline["label"])
    st.caption(baseline["warning"])
    st.markdown("#### EACT-v1 — single disposition")
    st.metric("Primary result", v1["label"])
    st.caption(v1["explanation"])

with right:
    st.markdown("#### EACT-v2 — multi-finding assessment")
    st.metric("Primary disposition", v2["label"])
    st.caption(
        f"{v2['finding_count']} findings • "
        f"{v2['evidence_dimensions_assessed']}/5 dimensions explicitly assessed"
    )
    st.write(v2["explanation"])
    st.markdown("**Recommended next step**")
    st.write(v2["next_action"])

st.markdown("### Independent findings")
if v2["findings"]:
    findings_rows = []
    for finding in v2["findings"]:
        findings_rows.append({
            "Finding": finding["label"],
            "Severity": finding["severity"].upper(),
            "Evidence dimension": finding["dimension"],
            "Supplied value": finding["supplied_value"],
            "Authority / limitation": finding["authority"],
        })
    st.dataframe(pd.DataFrame(findings_rows), use_container_width=True, hide_index=True)

    for index, finding in enumerate(v2["findings"], start=1):
        with st.expander(f"{index}. {finding['label']} — provenance and next action"):
            st.write(finding["detail"])
            st.caption(f"Evidence basis: {finding['authority']}")
            st.caption(f"Provenance: {finding['provenance']}")
            st.write("**Next action:** " + finding["next_action"])
else:
    st.success("No adverse or incomplete findings were generated from the supplied scenario.")

st.caption(v2["provenance_note"])

st.divider()
st.subheader("EACT-v2 results across the seven conflict scenarios")

with b2_path.open("r", encoding="utf-8") as source:
    b2_cases = json.load(source)["cases"]

b2_rows = []
for item in b2_cases:
    result = evaluate_evidence_v2(
        integrity=item["integrity"],
        issuer_identity=item["issuer_identity"],
        credential_status=item["credential_status"],
        subject_match=item["subject_match"],
        source_state=item["source_state"],
    )
    b2_rows.append({
        "Case": item["id"],
        "Scenario": item["title"],
        "EACT-v1 result": evaluate_evidence(
            integrity=item["integrity"],
            issuer_identity=item["issuer_identity"],
            credential_status=item["credential_status"],
            subject_match=item["subject_match"],
            source_state=item["source_state"],
        )["label"],
        "EACT-v2 primary": result["label"],
        "Finding count": result["finding_count"],
        "Findings surfaced": "; ".join(f["label"] for f in result["findings"]) or "None",
    })

st.dataframe(pd.DataFrame(b2_rows), use_container_width=True, hide_index=True)

with st.expander("Research interpretation and limitations"):
    st.markdown(
        "- EACT-v2 retains one primary disposition but also lists independent findings.\n"
        "- Inactive status claims are treated as authenticated only when issuer identity is authenticated and the scenario source is available; otherwise the status is labelled an unauthenticated claim.\n"
        "- A matching hash does not establish issuer identity, subject match, or current status.\n"
        "- All inputs remain synthetic/manual assertions. There is no per-field cryptographic provenance, identity proofing, or live registry call.\n"
        "- The conflict-case outputs are a design hypothesis and require stakeholder review; they are not a universal hiring policy."
    )
