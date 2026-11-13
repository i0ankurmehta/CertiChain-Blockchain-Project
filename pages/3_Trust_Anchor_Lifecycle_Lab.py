import json
from pathlib import Path

import pandas as pd
import streamlit as st

from eact_trust_lifecycle import (
    build_audit_trail,
    evaluate_trust_lifecycle,
    verify_audit_trail,
)


st.title("EACT-B4 — Trust Anchor Lifecycle Lab")
st.caption("Key governance • Rotation • Revocation • Compromise • Historical evidence • Audit integrity")

st.warning(
    "Research prototype only. All keys, issuers, timestamps and events are fictional/manual. "
    "This page does not store private keys, validate real signatures, or contact trust registries."
)

root = Path(__file__).resolve().parents[1]
fixture_path = root / "research" / "EACT_B4_trust_lifecycle_scenarios.json"
with fixture_path.open("r", encoding="utf-8") as source:
    fixture = json.load(source)

scenarios = fixture["scenarios"]
scenario_map = {f'{case["id"]} — {case["title"]}': case for case in scenarios}
timestamp_sources = [
    "trusted_timestamp_authority",
    "qualified_timestamp_authority",
    "issuer_signed_timestamp",
    "client_clock",
    "unknown",
]
signature_states = ["valid", "invalid", "not_checked"]
timestamp_states = ["verified", "invalid", "not_checked"]
registry_states = ["trusted", "untrusted", "unknown"]
event_types = ["none", "rotated", "revoked", "compromised", "distrusted", "reinstated"]
event_sources = [
    "trusted_anchor_registry",
    "issuer_security_notice",
    "trusted_trust_list",
    "manual_claim",
    "unknown",
]

with st.sidebar:
    st.header("Scenario selection")
    selected_label = st.selectbox("Choose a fictional B4 case", list(scenario_map))
    case = scenario_map[selected_label]
    st.caption(case["id"])
    st.divider()
    st.caption("Every control is synthetic/manual. Edited values are evaluated, not written back to the fixture.")

    anchor_registered = st.checkbox(
        "Key is registered in the trust registry",
        value=case["anchor"]["registered"],
        key=f"b4_registered_{case['id']}",
    )
    registry_status = st.selectbox(
        "Trust registry assessment",
        registry_states,
        index=registry_states.index(case["anchor"]["registry_status"]),
        key=f"b4_registry_{case['id']}",
    )
    valid_from = st.text_input(
        "Key valid from (ISO-8601 UTC)",
        value=case["anchor"]["valid_from"],
        key=f"b4_valid_from_{case['id']}",
    )
    expires_at = st.text_input(
        "Key expires at (ISO-8601 UTC)",
        value=case["anchor"]["expires_at"],
        key=f"b4_expires_{case['id']}",
    )

    signature_status = st.selectbox(
        "Credential signature result",
        signature_states,
        index=signature_states.index(case["verification"]["signature_status"]),
        key=f"b4_sig_{case['id']}",
    )
    signed_at = st.text_input(
        "Credential signed at (ISO-8601 UTC)",
        value=case["verification"]["signed_at"],
        key=f"b4_signed_at_{case['id']}",
    )
    timestamp_source = st.selectbox(
        "Signing-time source",
        timestamp_sources,
        index=timestamp_sources.index(case["verification"]["timestamp_source"]),
        key=f"b4_time_source_{case['id']}",
    )
    timestamp_signature_status = st.selectbox(
        "Timestamp-token signature result",
        timestamp_states,
        index=timestamp_states.index(case["verification"]["timestamp_signature_status"]),
        key=f"b4_time_sig_{case['id']}",
    )

    original_event = case["lifecycle_events"][0] if case["lifecycle_events"] else None
    st.divider()
    st.subheader("Lifecycle event")
    event_type_default = original_event["event_type"] if original_event else "none"
    event_type = st.selectbox(
        "Event type",
        event_types,
        index=event_types.index(event_type_default),
        key=f"b4_event_type_{case['id']}",
    )
    lifecycle_events = []
    if event_type != "none":
        source_default = original_event["source"] if original_event else "trusted_anchor_registry"
        authority_default = original_event["authority_status"] if original_event else "authenticated"
        event_sig_default = original_event["event_signature_status"] if original_event else "verified"
        effective_default = original_event["effective_at"] if original_event else "2026-06-01T00:00:00Z"
        recorded_default = original_event["recorded_at"] if original_event else effective_default
        event_source = st.selectbox(
            "Event source",
            event_sources,
            index=event_sources.index(source_default),
            key=f"b4_event_source_{case['id']}",
        )
        authority_status = st.selectbox(
            "Event authority",
            ["authenticated", "unverified"],
            index=["authenticated", "unverified"].index(authority_default),
            key=f"b4_event_authority_{case['id']}",
        )
        event_signature_status = st.selectbox(
            "Event signature result",
            ["verified", "invalid", "not_checked"],
            index=["verified", "invalid", "not_checked"].index(event_sig_default),
            key=f"b4_event_sig_{case['id']}",
        )
        effective_at = st.text_input(
            "Event effective at (ISO-8601 UTC)",
            value=effective_default,
            key=f"b4_effective_{case['id']}",
        )
        recorded_at = st.text_input(
            "Event recorded at (ISO-8601 UTC)",
            value=recorded_default,
            key=f"b4_recorded_{case['id']}",
        )
        lifecycle_events.append({
            "event_id": original_event["event_id"] if original_event else "EV-EDITED",
            "event_type": event_type,
            "effective_at": effective_at,
            "recorded_at": recorded_at,
            "source": event_source,
            "authority_status": authority_status,
            "event_signature_status": event_signature_status,
            "reason": original_event.get("reason", "operator_edited") if original_event else "operator_edited",
        })

anchor = {
    **case["anchor"],
    "registered": anchor_registered,
    "registry_status": registry_status,
    "valid_from": valid_from,
    "expires_at": expires_at,
}
verification = {
    **case["verification"],
    "signature_status": signature_status,
    "signed_at": signed_at,
    "timestamp_source": timestamp_source,
    "timestamp_signature_status": timestamp_signature_status,
}

fixture_inputs = {
    "anchor": case["anchor"],
    "lifecycle_events": case["lifecycle_events"],
    "verification": case["verification"],
}
current_inputs = {
    "anchor": anchor,
    "lifecycle_events": lifecycle_events,
    "verification": verification,
}
modified = current_inputs != fixture_inputs

st.subheader(f'{case["id"]} — {case["title"]}')
st.write(case["description"])
if modified:
    st.warning("Modified test configuration: results use your edited inputs, not the original fixture.")
else:
    st.success("Using the selected fixture's original evidence values.")

with st.expander("Exact trust-anchor and verification metadata used"):
    st.json(current_inputs)

assessment_time = fixture["assessment_time"]
result = evaluate_trust_lifecycle(
    anchor=anchor,
    lifecycle_events=lifecycle_events,
    verification=verification,
    assessment_time=assessment_time,
)

left, right = st.columns(2)
with left:
    st.markdown("#### Historical verification assessment")
    st.metric("B4 primary disposition", result["label"])
    st.write(result["explanation"])
    st.markdown("**Recommended next step**")
    st.write(result["next_action"])
with right:
    st.markdown("#### Trust and key lifecycle")
    trust_label = (
        "Trusted"
        if result["anchor_trusted"]
        else f'Not established ({anchor["registry_status"]})'
    )
    st.metric("Trust registry status", trust_label)
    st.metric(
        "Current key lifecycle state (metadata)",
        result["current_key_state"].replace("_", " ").title(),
    )
    if not result["anchor_trusted"]:
        st.warning(
            "The lifecycle state is inferred from supplied validity dates and accepted "
            "events only. It does not establish that this key belongs to a trusted issuer "
            "or may be used for verification."
        )
    st.metric(
        "Key lifecycle state at signing (metadata)",
        result["historical_key_state_at_signing"].replace("_", " ").title(),
    )
    if not result["timestamp_trusted"]:
        st.info(
            "Signing-time ordering is not established. The historical key state must be "
            "treated as unknown, regardless of the manually supplied date."
        )
    st.caption(
        f'Trusted signing time: {"Yes" if result["timestamp_trusted"] else "No"} · '
        f'Trusted lifecycle events: {result["trusted_event_count"]} · '
        f'Unverified events: {result["untrusted_event_count"]}'
    )

st.markdown("### Independent governance and lifecycle findings")
if result["findings"]:
    rows = [{
        "Finding": item["label"],
        "Severity": item["severity"].upper(),
        "Dimension": item["dimension"],
        "Supplied value": item["supplied_value"],
    } for item in result["findings"]]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    for index, item in enumerate(result["findings"], start=1):
        with st.expander(f'{index}. {item["label"]} — details'):
            st.write(item["detail"])
            st.write("**Next action:** " + item["next_action"])
            st.caption(item["provenance_note"])
else:
    st.success("No trust-anchor lifecycle findings were raised.")

st.caption(result["provenance_note"])

st.divider()
st.subheader("Append-only audit-chain demonstration")
st.caption(
    "This is a session-generated hash-linked demonstration. A hash chain can reveal "
    "record alteration against a trusted checkpoint, but it does not make storage immutable."
)

audit_records = [{
    "event_id": "AUD-REGISTER",
    "event": "anchor_registered",
    "key_id": anchor["key_id"],
    "fingerprint": anchor["fingerprint"],
    "recorded_at": anchor.get("valid_from"),
}]
for event in lifecycle_events:
    audit_records.append({
        "event_id": event["event_id"],
        "event": event["event_type"],
        "key_id": anchor["key_id"],
        "effective_at": event["effective_at"],
        "recorded_at": event["recorded_at"],
        "source": event["source"],
        "authority_status": event["authority_status"],
    })
audit_records.append({
    "event_id": "AUD-VERIFY",
    "event": "credential_verification",
    "credential_id": verification["credential_id"],
    "key_id": anchor["key_id"],
    "signed_at": verification["signed_at"],
    "signature_status": verification["signature_status"],
})

audit_trail = build_audit_trail(audit_records)
simulate_tampering = st.checkbox("Simulate an audit-record alteration", value=False)
if simulate_tampering and len(audit_trail) > 1:
    audit_trail[1]["record"]["event"] = "unauthorised_event_substitution"

audit_result = verify_audit_trail(audit_trail)
if audit_result["valid"]:
    st.success(f'Audit chain valid — {len(audit_trail)} records verified.')
else:
    st.error(
        f'Audit-chain integrity failure at record {audit_result["first_invalid_index"]}: '
        f'{audit_result["reason"]}.'
    )

audit_rows = [{
    "Sequence": item["sequence"],
    "Event": item["record"]["event"],
    "Previous hash": item["previous_hash"][:18] + "...",
    "Record hash": item["record_hash"][:18] + "...",
} for item in audit_trail]
st.dataframe(pd.DataFrame(audit_rows), use_container_width=True, hide_index=True)

st.divider()
st.subheader("B4 scenario matrix — all predefined fixtures")
matrix = []
for fixture_case in scenarios:
    fixture_result = evaluate_trust_lifecycle(
        anchor=fixture_case["anchor"],
        lifecycle_events=fixture_case["lifecycle_events"],
        verification=fixture_case["verification"],
        assessment_time=fixture["assessment_time"],
    )
    matrix.append({
        "Case": fixture_case["id"],
        "Scenario": fixture_case["title"],
        "Expected disposition": fixture_case["expected_disposition"],
        "Actual disposition": fixture_result["disposition"],
        "Matches fixture rule": fixture_result["disposition"] == fixture_case["expected_disposition"],
        "Finding count": fixture_result["finding_count"],
        "Current key state": fixture_result["current_key_state"],
    })
matrix_df = pd.DataFrame(matrix)
st.dataframe(matrix_df, use_container_width=True, hide_index=True)
st.caption(
    f'Fixture conformance: {int(matrix_df["Matches fixture rule"].sum())}/'
    f'{len(matrix_df)} scenarios. This checks authored software rules, not real-world security accuracy.'
)

with st.expander("Research assumptions, standards context and limitations"):
    st.markdown(
        "- Routine rotation and expiry are distinguished from key compromise. A trusted timestamp can support historical ordering, but archival reliance depends on issuer policy.\n"
        "- The event's effective time and the time the event was recorded are separate fields. Delayed compromise reporting can create a retrospective review window.\n"
        "- A lifecycle event is used as authoritative only when its source, authority and event-signature metadata satisfy the prototype's configured rules. The app does not verify these facts.\n"
        "- The audit chain is tamper-evident only when compared with a trusted checkpoint; it is not immutable storage or a distributed consensus network.\n"
        "- NIST SP 800-57 Part 1 Rev. 5 is the current final guidance found for this research; Rev. 6 remains an initial public draft in the NIST catalogue. RFC 5280 distinguishes invalidity date from revocation date; RFC 6960 defines OCSP response validity-time fields.\n"
        "- All records are synthetic. No keys, university data, live certificates, issuer registry or timestamp authority are connected."
    )
