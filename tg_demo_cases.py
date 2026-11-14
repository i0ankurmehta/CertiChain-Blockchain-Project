"""Clearly fictional demonstration cases for the Trust Gatekeeper UI."""
from copy import deepcopy

DEMO_CASES = {
    "Later-session programme approval": {
        "case_id": "TG-DEMO-002",
        "description": "A programme is approved for 2022–2023, while the candidate claims admission in 2021–2022.",
        "processing_authority_documented": True, "input_safe": True,
        "input_mode": "paired", "entity_resolution_status": "resolved",
        "field_comparisons": [
            {"field": "programme", "submitted_value": "BBA", "extracted_value": "BBA", "ocr_confidence": 0.98},
            {"field": "admission_session", "submitted_value": "2021-2022", "extracted_value": "2021-2022", "ocr_confidence": 0.99},
        ],
        "required_claims": [
            {"claim_id": "CL-PROGRAMME-01", "scope": "programme_status", "subject_id": "SYN-RIVERGATE-BBA-ONLINE", "predicate": "approved_for_admission", "expected_value": "approved", "relevant_session": "2021-2022", "required_source_classes": ["B"]},
            {"claim_id": "CL-AWARD-01", "scope": "individual_award", "subject_id": "SYN-CANDIDATE-002", "predicate": "award_confirmed", "expected_value": "confirmed", "relevant_date": "2024-08-20", "required_source_classes": ["A"]},
        ],
        "evidence": [
            {"evidence_id": "SYN2-E01", "source_id": "SYN2-SRC-ORDER", "subject_id": "SYN-RIVERGATE-BBA-ONLINE", "predicate": "approved_for_admission", "claim_scope": "programme_status", "value": "approved", "source_class": "B", "review_state": "reviewed", "valid_sessions": ["2022-2023"], "excluded_sessions": ["2021-2022"], "period_scope_complete": True},
            {"evidence_id": "SYN2-E02", "source_id": "SYN2-SRC-REGISTER", "parent_source_id": "SYN2-SRC-ORDER", "subject_id": "SYN-RIVERGATE-BBA-ONLINE", "predicate": "approved_for_admission", "claim_scope": "programme_status", "value": "approved", "source_class": "B", "review_state": "reviewed", "valid_sessions": ["2022-2023"], "excluded_sessions": ["2021-2022"], "period_scope_complete": True},
            {"evidence_id": "SYN2-E03", "source_id": "SYN2-SRC-DIRECTORY-A", "parent_source_id": "SYN2-SRC-REGISTER", "subject_id": "SYN-RIVERGATE-BBA-ONLINE", "predicate": "approved_for_admission", "claim_scope": "programme_status", "value": "approved", "source_class": "D", "review_state": "reviewed", "valid_sessions": ["2022-2023"], "excluded_sessions": ["2021-2022"], "period_scope_complete": True},
            {"evidence_id": "SYN2-E04", "source_id": "SYN2-SRC-DIRECTORY-B", "parent_source_id": "SYN2-SRC-DIRECTORY-A", "subject_id": "SYN-RIVERGATE-BBA-ONLINE", "predicate": "approved_for_admission", "claim_scope": "programme_status", "value": "approved", "source_class": "D", "review_state": "reviewed", "valid_sessions": ["2022-2023"], "excluded_sessions": ["2021-2022"], "period_scope_complete": True},
        ],
    },
    "Affiliation transition ambiguity": {
        "case_id": "TG-DEMO-001",
        "description": "A college affiliation changes, but the continuing cohort's awarding authority is not established.",
        "processing_authority_documented": True, "input_safe": True,
        "input_mode": "paired", "entity_resolution_status": "ambiguous",
        "field_comparisons": [{"field": "awarding_institution", "submitted_value": "Aster State University", "extracted_value": "Aster State University", "ocr_confidence": 0.97}],
        "required_claims": [
            {"claim_id": "CL-COHORT-01", "scope": "cohort_awarding_authority", "subject_id": "SYN-NORTHBRIDGE-COHORT-2020", "predicate": "awarding_authority", "expected_value": "Aster State University", "relevant_date": "2023-08-15", "required_source_classes": ["B", "C"]},
            {"claim_id": "CL-AWARD-02", "scope": "individual_award", "subject_id": "SYN-CANDIDATE-001", "predicate": "award_confirmed", "expected_value": "confirmed", "relevant_date": "2023-08-15", "required_source_classes": ["A"]},
        ],
        "evidence": [
            {"evidence_id": "SYN-E01", "source_id": "SYN-SRC-ASTER-AFFILIATION", "subject_id": "SYN-NORTHBRIDGE", "predicate": "affiliated_with", "claim_scope": "college_affiliation", "value": "Aster State University", "source_class": "C", "review_state": "reviewed", "valid_sessions": ["2020-2021", "2021-2022"]},
            {"evidence_id": "SYN-E02", "source_id": "SYN-SRC-MERIDIAN-AFFILIATION", "subject_id": "SYN-NORTHBRIDGE", "predicate": "affiliated_with", "claim_scope": "college_affiliation", "value": "Meridian University", "source_class": "C", "review_state": "reviewed", "valid_sessions": ["2022-2023"]},
        ],
    },
    "Context supported, award unverified": {
        "case_id": "TG-DEMO-003",
        "description": "Institution/programme context is supported for the relevant session, but no award-specific issuer evidence is supplied.",
        "processing_authority_documented": True, "input_safe": True,
        "input_mode": "structured", "entity_resolution_status": "resolved", "field_comparisons": [],
        "required_claims": [
            {"claim_id": "CL-AFFILIATION-03", "scope": "college_affiliation", "subject_id": "SYN-COLLEGE-003", "predicate": "affiliated_with", "expected_value": "SYN-UNIVERSITY-003", "relevant_session": "2021-2022", "required_source_classes": ["C"]},
            {"claim_id": "CL-PROGRAMME-03", "scope": "programme_status", "subject_id": "SYN-PROGRAMME-003", "predicate": "approved_for_admission", "expected_value": "approved", "relevant_session": "2021-2022", "required_source_classes": ["B"]},
            {"claim_id": "CL-AWARD-03", "scope": "individual_award", "subject_id": "SYN-CANDIDATE-003", "predicate": "award_confirmed", "expected_value": "confirmed", "relevant_date": "2024-06-30", "required_source_classes": ["A"]},
        ],
        "evidence": [
            {"evidence_id": "SYN3-E01", "source_id": "SYN3-SRC-AFFILIATION", "subject_id": "SYN-COLLEGE-003", "predicate": "affiliated_with", "claim_scope": "college_affiliation", "value": "SYN-UNIVERSITY-003", "source_class": "C", "review_state": "reviewed", "valid_sessions": ["2021-2022"]},
            {"evidence_id": "SYN3-E02", "source_id": "SYN3-SRC-PROGRAMME", "subject_id": "SYN-PROGRAMME-003", "predicate": "approved_for_admission", "claim_scope": "programme_status", "value": "approved", "source_class": "B", "review_state": "reviewed", "valid_sessions": ["2021-2022"]},
        ],
    },
}


def get_demo_case(label: str) -> dict:
    if label not in DEMO_CASES:
        raise KeyError(f"Unknown demonstration case: {label}")
    return deepcopy(DEMO_CASES[label])
