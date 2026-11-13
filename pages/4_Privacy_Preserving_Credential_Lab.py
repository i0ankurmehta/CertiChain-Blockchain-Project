"""EACT-B5 interactive lab: purpose-bound academic credential disclosure."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import streamlit as st

from eact_privacy import (
    CLAIM_CATALOG,
    PREDICATES,
    PURPOSE_POLICIES,
    disclosure_matrix,
    evaluate_disclosure_request,
)


st.set_page_config(page_title="EACT-B5 Privacy-Preserving Credentials", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_FILE = ROOT / "research" / "EACT_B5_privacy_scenarios.json"


@st.cache_data
def load_scenarios():
    with FIXTURE_FILE.open("r", encoding="utf-8") as source:
        dataset = json.load(source)
    scenarios = dataset.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("The B5 scenario file must contain a non-empty scenarios list.")
    return dataset


try:
    DATASET = load_scenarios()
except (OSError, json.JSONDecodeError, ValueError, TypeError) as error:
    st.error(f"Could not load B5 synthetic scenarios: {error}")
    st.stop()


st.title("EACT-B5 — Privacy-Preserving Academic Credential Lab")
st.caption(
    "Purpose limitation • Minimum necessary claims • Holder consent • "
    "Selective disclosure • Linkability and re-identification"
)
st.warning(
    "Research prototype only. All people, institutions and credentials are fictional. "
    "This lab does not issue or verify real credentials, generate SD-JWTs or zero-knowledge "
    "proofs, contact issuers, or make hiring/admission decisions."
)

SCENARIOS = DATASET["scenarios"]
SCENARIO_BY_ID = {item["id"]: item for item in SCENARIOS}

with st.sidebar:
    st.header("Scenario selection")
    selected_id = st.selectbox(
        "Choose a fictional case",
        options=[item["id"] for item in SCENARIOS],
        format_func=lambda case_id: (
            f"{case_id} — {SCENARIO_BY_ID[case_id]['title']}"
        ),
    )
    scenario = copy.deepcopy(SCENARIO_BY_ID[selected_id])
    st.caption(scenario["summary"])
    st.divider()

    st.header("1. Verifier request")
    purpose_options = list(PURPOSE_POLICIES)
    if scenario["purpose"] not in purpose_options:
        purpose_options.append(scenario["purpose"])
    purpose = st.selectbox(
        "Declared verification purpose",
        options=purpose_options,
        index=purpose_options.index(scenario["purpose"]),
        format_func=lambda value: (
            PURPOSE_POLICIES[value]["label"]
            if value in PURPOSE_POLICIES
            else f"Unsupported: {value}"
        ),
    )
    requested_claims = st.multiselect(
        "Claims requested",
        options=list(CLAIM_CATALOG),
        default=scenario.get("requested_claims", []),
        format_func=lambda key: CLAIM_CATALOG[key]["label"],
        help="The verifier's requested attributes. The purpose policy defines the minimum and allowed set.",
    )
    requested_predicates = st.multiselect(
        "Threshold / predicate requests",
        options=list(PREDICATES),
        default=scenario.get("requested_predicates", []),
        format_func=lambda key: PREDICATES[key]["label"],
        help="A predicate result can disclose whether a threshold is met without displaying the raw CGPA. This is simulated, not a cryptographic proof.",
    )
    secondary_use = st.text_input(
        "Additional or secondary use (leave blank for none)",
        value=scenario.get("secondary_use", ""),
    )
    retention_was_specified = st.checkbox(
        "Verifier specifies a retention period",
        value=scenario.get("retention_days") is not None,
    )
    if retention_was_specified:
        retention_days = st.number_input(
            "Retention period (days)",
            min_value=0,
            max_value=3650,
            value=int(scenario.get("retention_days") or 30),
            step=1,
        )
    else:
        retention_days = None

    st.divider()
    st.header("2. Holder choice and issuer context")
    approved_claims = st.multiselect(
        "Claims approved by holder",
        options=list(CLAIM_CATALOG),
        default=scenario.get("approved_claims", []),
        format_func=lambda key: CLAIM_CATALOG[key]["label"],
        help="Only claims both requested and holder-approved appear in the presentation proposal.",
    )
    approved_predicates = st.multiselect(
        "Predicates approved by holder",
        options=list(PREDICATES),
        default=scenario.get("approved_predicates", []),
        format_func=lambda key: PREDICATES[key]["label"],
    )
    issuer_trust = st.selectbox(
        "Issuer trust assertion",
        ["trusted", "untrusted", "unknown"],
        index=["trusted", "untrusted", "unknown"].index(
            scenario["credential"].get("issuer_trust", "unknown")
        ),
    )
    credential_status = st.selectbox(
        "Credential status assertion",
        ["active", "revoked", "expired", "unknown"],
        index=["active", "revoked", "expired", "unknown"].index(
            scenario["credential"].get("credential_status", "unknown")
        ),
    )
    st.caption("Presentation history is synthetic fixture context and is not fetched from any service.")


credential = scenario["credential"]
result = evaluate_disclosure_request(
    scenario,
    purpose=purpose,
    requested_claims=requested_claims,
    approved_claims=approved_claims,
    requested_predicates=requested_predicates,
    approved_predicates=approved_predicates,
    issuer_trust=issuer_trust,
    credential_status=credential_status,
    secondary_use=secondary_use,
    retention_days=retention_days,
)

st.markdown(f"### {selected_id} — {scenario['title']}")
st.write(scenario["summary"])

left, right = st.columns(2)
with left:
    st.markdown("#### Verification outcome")
    st.metric("Disposition", result["disposition"].replace("_", " ").title())
    st.write(result["message"])
    if result["can_verify_purpose"]:
        st.success("Synthetic evidence is sufficient for the selected purpose policy.")
    elif result["disposition"] == "secondary_use_requires_review":
        st.warning(
            "The minimum evidence is present for the primary purpose, but the stated "
            "secondary use is not approved under this policy."
        )
    elif result["disposition"] == "purpose_not_supported":
        st.error("No reviewed purpose-specific policy exists; no claims are proposed.")
    elif result["disposition"] in {"issuer_trust_not_established", "credential_status_not_active"}:
        st.error("Issuer trust or credential status is not established; no presentation is proposed.")
    else:
        st.error("The selected purpose cannot be completed on the supplied synthetic evidence.")
with right:
    st.markdown("#### Disclosure footprint")
    st.metric(
        "Claims in proposed presentation",
        f"{result['proposed_claim_count']} / {result['full_credential_claim_count']}",
    )
    if result["exposure_reduction_assessed"]:
        st.metric(
            "Heuristic exposure reduction",
            f"{result['exposure_reduction_percent']:.1f}%",
        )
        st.caption(
            f"Exposure units: {result['proposed_exposure_units']} proposed vs "
            f"{result['full_credential_exposure_units']} in the full-record baseline. "
            "These are illustrative weights, not a validated privacy metric."
        )
    else:
        st.metric("Heuristic exposure reduction", "Not assessed")
        st.caption(
            "No valid presentation proposal was generated, so disclosure reduction "
            "is not scored for this case."
        )

if result["presentation_ready"]:
    st.success("Minimum presentation is complete and has no flagged privacy issue under this prototype policy.")
elif result["disposition"] == "secondary_use_requires_review":
    st.warning(
        "The primary-purpose minimum is present, but no presentation should be completed "
        "until the secondary use is removed or separately reviewed."
    )
elif result["can_verify_purpose"]:
    st.warning(
        "The minimum evidence may satisfy the purpose, but privacy findings remain. "
        "Trim the request or resolve the review items before any real presentation."
    )
else:
    st.info(
        "No completed presentation is recommended. The holder may decline; the verifier "
        "must not infer fraud from withheld optional information."
    )

st.markdown("### Purpose-specific minimum")
policy = PURPOSE_POLICIES.get(purpose)
if policy:
    st.caption(policy["description"])
    required_labels = [CLAIM_CATALOG[key]["label"] for key in policy["required_claims"]]
    st.write("**Minimum claims:** " + ", ".join(required_labels))
    if policy["required_predicates"]:
        predicate_labels = [PREDICATES[key]["label"] for key in policy["required_predicates"]]
        st.write("**Required predicate(s):** " + ", ".join(predicate_labels))
else:
    st.write("No purpose-specific minimum has been defined. This scenario fails closed.")

st.markdown("### Presentation proposal — only requested and holder-approved claims")
if result["proposed_claims"]:
    proposal_rows = []
    for key, value in result["proposed_claims"].items():
        proposal_rows.append({
            "Claim": CLAIM_CATALOG[key]["label"],
            "Value in synthetic presentation": (
                json.dumps(value, sort_keys=True)
                if isinstance(value, (dict, list))
                else str(value)
            ),
            "Sensitivity": CLAIM_CATALOG[key]["sensitivity"].title(),
            "Required by policy": "Yes" if key in result["minimum_required_claims"] else "No",
        })
    st.dataframe(proposal_rows, use_container_width=True, hide_index=True)
else:
    st.info("No claim values are proposed for presentation.")

if result["predicate_results"]:
    st.markdown("### Predicate results — simulated, not zero-knowledge proofs")
    for item in result["predicate_results"]:
        if item["satisfied"] is True:
            st.success(f"{item['label']}: SATISFIED")
        elif item["satisfied"] is False:
            st.error(f"{item['label']}: NOT SATISFIED")
        else:
            st.warning(f"{item['label']}: NO RESULT")
    st.caption(
        "The engine evaluates the hidden synthetic CGPA in memory and exposes only the "
        "threshold outcome in this presentation proposal. No ZK proof or SD-JWT is generated."
    )

st.markdown("### Independent privacy and sufficiency findings")
if result["findings"]:
    finding_rows = [{
        "Finding": item["label"],
        "Severity": item["severity"].upper(),
        "Dimension": item["dimension"],
        "Supplied value": item["supplied_value"],
    } for item in result["findings"]]
    st.dataframe(finding_rows, use_container_width=True, hide_index=True)
    for index, item in enumerate(result["findings"], start=1):
        with st.expander(f"{index}. {item['label']} — details"):
            st.write(item["detail"])
            st.write("**Recommended next step:** " + item["next_action"])
else:
    st.success("No additional privacy or sufficiency finding was raised for this synthetic case.")

st.markdown("### Full-record baseline versus selected presentation")
full_claim_rows = []
for key, value in credential["claims"].items():
    full_claim_rows.append({
        "Claim": CLAIM_CATALOG[key]["label"],
        "Sensitivity": CLAIM_CATALOG[key]["sensitivity"].title(),
        "Value in full synthetic record": (
            json.dumps(value, sort_keys=True)
            if isinstance(value, (dict, list))
            else str(value)
        ),
        "In presentation proposal": "Yes" if key in result["proposed_claims"] else "No",
    })
with st.expander("Inspect the entire fictional academic record"):
    st.dataframe(full_claim_rows, use_container_width=True, hide_index=True)
    st.caption("The full record is shown only to make the disclosure difference inspectable; it is not sent anywhere.")

with st.expander("Claim-by-claim request and consent matrix"):
    st.dataframe(disclosure_matrix(result), use_container_width=True, hide_index=True)

st.markdown("### B5 scenario matrix — original synthetic fixtures")
matrix_rows = []
for case in SCENARIOS:
    case_result = evaluate_disclosure_request(case)
    matrix_rows.append({
        "Case": case["id"],
        "Scenario": case["title"],
        "Expected disposition": case["expected_disposition"],
        "Actual disposition": case_result["disposition"],
        "Matches fixture": "Yes" if case_result["disposition"] == case["expected_disposition"] else "No",
        "Proposed claims": case_result["proposed_claim_count"],
        "Findings": len(case_result["findings"]),
    })
st.dataframe(matrix_rows, use_container_width=True, hide_index=True)
matches = sum(row["Matches fixture"] == "Yes" for row in matrix_rows)
st.caption(
    f"Fixture conformance: {matches}/{len(matrix_rows)}. This checks deterministic software "
    "outputs against authored synthetic cases, not real-world privacy or verification accuracy."
)

with st.expander("Research interpretation, standards and limitations"):
    st.markdown(
        """
        **Design distinction**

        - W3C Verifiable Credentials Data Model 2.0 defines a credential data model and ecosystem; it does not by itself make this lab's filtered JSON a cryptographic selective-disclosure proof.
        - IETF RFC 9901 specifies selective disclosure for JWT claims.
        - OpenID4VP 1.0 defines a protocol for requesting and presenting credentials.
        - SD-JWT VC is still an Internet-Draft in the current research snapshot; check its status before implementation decisions.

        **Prototype limitations**

        - All identities, issuers, claims, verifier purposes, consent choices and results are synthetic.
        - The purpose policies and sensitivity weights are research assumptions, not law or universal hiring rules.
        - The threshold result is calculated from the hidden fixture value. No zero-knowledge proof, selective-disclosure cryptography, holder key binding or signed presentation is implemented.
        - The lab does not verify issuer signatures, credential status, consent authenticity, identity binding or verifier authorisation.
        - A presentation can still leak information through repeated requests, timestamps, issuer metadata, rare attribute combinations or stable identifiers.
        """
    )
    st.markdown(
        "[W3C VC Data Model 2.0](https://www.w3.org/TR/vc-data-model/) · "
        "[IETF RFC 9901](https://www.rfc-editor.org/rfc/rfc9901.html) · "
        "[OpenID4VP 1.0](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html) · "
        "[SD-JWT VC status](https://datatracker.ietf.org/doc/draft-ietf-oauth-sd-jwt-vc/)"
    )
