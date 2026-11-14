"""CertiChain Trust Gatekeeper — synthetic research prototype UI."""

import json
from datetime import datetime, timezone

import streamlit as st

from tg_demo_cases import DEMO_CASES, get_demo_case
from tg_rules import OUTCOME_LABELS, assess_case


st.set_page_config(
    page_title="CertiChain | Trust Gatekeeper",
    page_icon="🧭",
    layout="wide",
)

st.title("CertiChain | Trust Gatekeeper")
st.caption("Temporal and provenance-aware academic credential evidence triage")
st.warning(
    "RESEARCH PROTOTYPE — synthetic fixtures only. Do not upload or enter real candidate, "
    "student, university or personal data. This tool does not authenticate an individual award."
)

with st.sidebar:
    st.header("Synthetic case")
    selected_case = st.selectbox("Choose a demonstration case", list(DEMO_CASES))
    demo_case = get_demo_case(selected_case)
    st.caption(demo_case["description"])
    st.divider()
    st.subheader("Intake gates")
    authority_ok = st.checkbox("Processing authority documented (fixture)", value=True)
    input_safe = st.checkbox("Input passed safety checks (fixture)", value=True)
    st.caption("These controls test the intake gate. They are not a legal consent workflow.")

case = get_demo_case(selected_case)
case["processing_authority_documented"] = authority_ok
case["input_safe"] = input_safe
assessment = assess_case(case)

primary = assessment["primary_outcome"]
primary_label = assessment["primary_label"]

summary_cols = st.columns(4)
summary_cols[0].metric("Case ID", assessment["case_id"])
summary_cols[1].metric("Primary finding", primary)
summary_cols[2].metric("Assessment state", assessment["case_state"].replace("_", " ").title())
summary_cols[3].metric("Human review", "Required" if assessment["review_required"] else "Not required")

st.subheader(primary_label)
st.write(assessment["explanation"])
if primary == "EV-01":
    st.success("The scoped contextual checks are consistent. Individual award verification remains a separate check.")
elif primary == "EV-07":
    st.error("Intake is blocked. No substantive evidence assessment was performed.")
else:
    st.warning("This is a preliminary evidence finding, not a fraud verdict or candidate decision.")

if assessment["secondary_findings"]:
    st.write("**Additional findings:** " + ", ".join(
        f"{code} — {OUTCOME_LABELS[code]}" for code in assessment["secondary_findings"]
    ))

st.subheader("Claim-by-claim assessment")
if assessment["scope_results"]:
    st.dataframe(
        [
            {
                "Claim ID": row["claim_id"],
                "Scope": row["scope"],
                "Outcome": row["outcome"],
                "Finding": row["label"],
                "Evidence IDs": ", ".join(row["evidence_ids"]) or "None",
                "Explanation": row["explanation"],
            }
            for row in assessment["scope_results"]
        ],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No claim-level checks were run because intake is blocked.")

st.subheader("Source lineage")
if assessment["dependency_groups"]:
    st.dataframe(
        [
            {
                "Lineage root": group["root_source_id"],
                "Source IDs": ", ".join(group["source_ids"]),
                "Evidence IDs": ", ".join(group["evidence_ids"]),
                "Relationship": group["relationship"],
            }
            for group in assessment["dependency_groups"]
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.caption("Related sources are grouped by known parent-source lineage; they are not counted as independent confirmations.")
else:
    st.info("No known multi-source lineage group was identified. Unknown dependency is not assumed to be independence.")

left, right = st.columns(2)
with left:
    st.subheader("Unresolved questions")
    if assessment["unresolved_questions"]:
        for item in assessment["unresolved_questions"]:
            st.markdown(f"- {item}")
    else:
        st.write("No unresolved question was produced for this synthetic fixture.")
with right:
    st.subheader("Recommended next actions")
    if assessment["recommended_actions"]:
        for item in assessment["recommended_actions"]:
            st.markdown(f"- {item}")
    else:
        st.write("No additional action was produced.")

with st.expander("Inspect synthetic case evidence and inputs"):
    st.markdown(f"**Input mode:** `{case.get('input_mode', 'not specified')}`")
    st.markdown("**Field comparisons**")
    st.dataframe(case.get("field_comparisons", []), use_container_width=True, hide_index=True)
    st.markdown("**Required claims**")
    st.json(case.get("required_claims", []))
    st.markdown("**Evidence records**")
    st.json(case.get("evidence", []))

with st.expander("Inspect complete assessment output"):
    st.json(assessment)

report = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "case_fixture": case,
    "assessment": assessment,
}
st.download_button(
    "Download synthetic assessment JSON",
    data=json.dumps(report, indent=2, ensure_ascii=False),
    file_name=f"{assessment['case_id'].lower()}_assessment.json",
    mime="application/json",
)

st.divider()
st.caption(
    "TG-RULES-001 v0.1 · Synthetic-only · Human review required for unresolved findings. "
    "Actual PDF/image upload, OCR, source ingestion and issuer verification are not implemented yet."
)
