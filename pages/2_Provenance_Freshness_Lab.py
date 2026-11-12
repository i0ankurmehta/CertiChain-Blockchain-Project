import json
from pathlib import Path

import pandas as pd
import streamlit as st

from eact_provenance import (
    DEFAULT_MAX_ISSUER_AUTH_AGE_DAYS,
    DEFAULT_MAX_STATUS_AGE_HOURS,
    evaluate_provenance,
)


st.title("EACT-B3 — Provenance & Freshness Lab")
st.caption("Evidence source, authentication history, timestamps and freshness • Synthetic research experiment")

st.warning(
    "Research prototype only. All records and source states are fictional/manual. "
    "This page does not validate real signatures, contact issuers, or connect to registries."
)

root = Path(__file__).resolve().parents[1]
fixture_path = root / "research" / "EACT_B3_provenance_scenarios.json"
with fixture_path.open("r", encoding="utf-8") as source:
    fixture = json.load(source)

scenarios = fixture["scenarios"]
scenario_map = {f'{case["id"]} — {case["title"]}': case for case in scenarios}

reference_origins = [
    "issuer_signed_manifest",
    "trusted_registry_export",
    "local_database",
    "student_uploaded_hash",
    "unknown",
]
signature_options = ["verified", "invalid", "not_checked"]
authentication_options = ["authenticated", "unverified"]
issuer_sources = ["trusted_issuer_directory", "manual_claim", "unknown"]
status_values = ["active", "revoked", "suspended", "expired", "unknown"]
status_sources = ["issuer_status_api", "signed_registry_snapshot", "manual_claim", "unknown"]

with st.sidebar:
    st.header("Scenario selection")
    chosen = st.selectbox("Select a fictional B3 case", list(scenario_map))
    case = scenario_map[chosen]
    st.caption(case["id"])
    st.divider()
    st.caption("All controls are editable. The assessment uses the current sidebar values.")

    integrity = st.selectbox(
        "Integrity comparison",
        ["match", "mismatch", "not_checked"],
        index=["match", "mismatch", "not_checked"].index(case["integrity_result"]),
        key=f"b3_integrity_{case['id']}",
    )
    ref_origin = st.selectbox(
        "Reference-hash origin",
        reference_origins,
        index=reference_origins.index(case["reference_origin"]),
        key=f"b3_ref_origin_{case['id']}",
    )
    ref_signature = st.selectbox(
        "Reference signature check",
        signature_options,
        index=signature_options.index(case["reference_signature_status"]),
        key=f"b3_ref_signature_{case['id']}",
    )
    issuer_auth = st.selectbox(
        "Issuer authentication state",
        authentication_options,
        index=authentication_options.index(case["issuer_authentication_status"]),
        key=f"b3_issuer_auth_{case['id']}",
    )
    issuer_source = st.selectbox(
        "Issuer authentication source",
        issuer_sources,
        index=issuer_sources.index(case["issuer_auth_source"]),
        key=f"b3_issuer_source_{case['id']}",
    )
    issuer_timestamp_available = st.checkbox(
        "Issuer-authentication timestamp available",
        value=case["issuer_auth_age_days"] is not None,
        key=f"b3_issuer_time_available_{case['id']}",
    )
    issuer_age = None
    if issuer_timestamp_available:
        issuer_age = st.number_input(
            "Issuer authentication age (days)",
            min_value=0.0,
            max_value=3650.0,
            value=float(case["issuer_auth_age_days"] or 0.0),
            step=1.0,
            key=f"b3_issuer_age_{case['id']}",
        )

    credential_status = st.selectbox(
        "Credential status value",
        status_values,
        index=status_values.index(case["credential_status"]),
        key=f"b3_status_{case['id']}",
    )
    status_source = st.selectbox(
        "Credential-status source",
        status_sources,
        index=status_sources.index(case["status_source_type"]),
        key=f"b3_status_source_{case['id']}",
    )
    status_auth = st.selectbox(
        "Status-source authentication",
        authentication_options,
        index=authentication_options.index(case["status_source_authentication"]),
        key=f"b3_status_auth_{case['id']}",
    )
    status_timestamp_available = st.checkbox(
        "Credential-status timestamp available",
        value=case["status_checked_age_hours"] is not None,
        key=f"b3_status_time_available_{case['id']}",
    )
    status_age = None
    if status_timestamp_available:
        status_age = st.number_input(
            "Status-check age (hours)",
            min_value=0.0,
            max_value=87600.0,
            value=float(case["status_checked_age_hours"] or 0.0),
            step=1.0,
            key=f"b3_status_age_{case['id']}",
        )

inputs = {
    "integrity_result": integrity,
    "reference_origin": ref_origin,
    "reference_signature_status": ref_signature,
    "issuer_authentication_status": issuer_auth,
    "issuer_auth_source": issuer_source,
    "issuer_auth_age_days": issuer_age,
    "credential_status": credential_status,
    "status_source_type": status_source,
    "status_source_authentication": status_auth,
    "status_checked_age_hours": status_age,
}

fixture_inputs = {
    key: case[key]
    for key in inputs
}
modified = inputs != fixture_inputs

st.subheader(f'{case["id"]} — {case["title"]}')
st.write(case["description"])
if modified:
    st.warning("Modified test configuration: results use the edited controls, not the original fixture values.")
else:
    st.success("Using the selected fixture's original evidence values.")

with st.expander("Exact evidence metadata used"):
    st.json(inputs)

assessment = evaluate_provenance(**inputs)

left, right = st.columns(2)
with left:
    st.markdown("#### Primary disposition")
    st.metric("EACT-B3 result", assessment["label"])
    st.write(assessment["explanation"])
    st.markdown("**Recommended next step**")
    st.write(assessment["next_action"])

with right:
    st.markdown("#### Evidence freshness")
    st.metric(
        "Issuer-authentication evidence",
        assessment["issuer_freshness"].replace("_", " ").title(),
    )
    st.metric(
        "Credential-status evidence",
        assessment["status_freshness"].replace("_", " ").title(),
    )
    st.caption(
        f"Experimental thresholds: issuer authentication ≤ "
        f"{assessment['thresholds']['max_issuer_auth_age_days']:g} days; "
        f"status evidence ≤ {assessment['thresholds']['max_status_age_hours']:g} hours."
    )

st.markdown("### Independent provenance and freshness findings")
if assessment["findings"]:
    rows = [
        {
            "Finding": finding["label"],
            "Severity": finding["severity"].upper(),
            "Dimension": finding["dimension"],
            "Supplied value": finding["supplied_value"],
            "Source": finding["source"],
            "Freshness": finding["freshness"].replace("_", " ").title(),
        }
        for finding in assessment["findings"]
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    for index, finding in enumerate(assessment["findings"], start=1):
        with st.expander(f'{index}. {finding["label"]} — details'):
            st.write(finding["detail"])
            st.caption(f'Evidence source: {finding["source"]}')
            st.caption(f'Freshness assessment: {finding["freshness"]}')
            st.caption(f'Provenance: {finding["provenance_note"]}')
            st.write("**Next action:** " + finding["next_action"])
else:
    st.success("No provenance or freshness issues were raised by the supplied synthetic inputs.")

st.caption(assessment["provenance_note"])

st.divider()
st.subheader("B3 scenario matrix — all predefined fixtures")
matrix = []
for fixture_case in scenarios:
    result = evaluate_provenance(
        integrity_result=fixture_case["integrity_result"],
        reference_origin=fixture_case["reference_origin"],
        reference_signature_status=fixture_case["reference_signature_status"],
        issuer_authentication_status=fixture_case["issuer_authentication_status"],
        issuer_auth_source=fixture_case["issuer_auth_source"],
        issuer_auth_age_days=fixture_case["issuer_auth_age_days"],
        credential_status=fixture_case["credential_status"],
        status_source_type=fixture_case["status_source_type"],
        status_source_authentication=fixture_case["status_source_authentication"],
        status_checked_age_hours=fixture_case["status_checked_age_hours"],
    )
    matrix.append({
        "Case": fixture_case["id"],
        "Scenario": fixture_case["title"],
        "Expected disposition": fixture_case["expected_disposition"],
        "Actual disposition": result["disposition"],
        "Matches fixture rule": result["disposition"] == fixture_case["expected_disposition"],
        "Finding count": result["finding_count"],
    })

matrix_df = pd.DataFrame(matrix)
st.dataframe(matrix_df, use_container_width=True, hide_index=True)
st.caption(
    f"Fixture conformance: {int(matrix_df['Matches fixture rule'].sum())}/"
    f"{len(matrix_df)} predefined scenarios. This checks implementation against "
    "authored expected outputs, not real-world verification accuracy."
)

with st.expander("Research assumptions and limits"):
    st.markdown(
        "- The 90-day issuer-authentication threshold and 24-hour status threshold are experimental defaults chosen for this study; they require stakeholder and issuer-specific calibration.\n"
        "- Hashes do not establish the provenance of the reference digest. The reference origin and signature state are separate inputs.\n"
        "- A revoked claim is treated as confirmed only when the scenario marks its status source as authenticated and current.\n"
        "- A stale or unavailable status record is not treated as proof that a credential is fraudulent or revoked.\n"
        "- The app does not verify cryptographic signatures, issuer directories, source timestamps, or registry records. All values are synthetic/manual."
    )
