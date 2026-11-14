import unittest

from tg_demo_cases import get_demo_case
from tg_rules import EV01, EV02, EV03, EV04, EV05, EV06, EV07, assess_case


def base_case():
    return {
        "case_id": "TEST-001",
        "processing_authority_documented": True,
        "input_safe": True,
        "entity_resolution_status": "resolved",
        "field_comparisons": [],
        "required_claims": [],
        "evidence": [],
    }


def claim(**overrides):
    result = {
        "claim_id": "C1", "scope": "programme_status", "subject_id": "P1",
        "predicate": "approved", "expected_value": "yes", "relevant_session": "2021-2022",
        "required_source_classes": ["B"],
    }
    result.update(overrides)
    return result


def evidence(**overrides):
    result = {
        "evidence_id": "E1", "source_id": "S1", "subject_id": "P1",
        "predicate": "approved", "claim_scope": "programme_status", "value": "yes",
        "source_class": "B", "review_state": "reviewed", "valid_sessions": ["2021-2022"],
    }
    result.update(overrides)
    return result


class TestTrustGatekeeperRules(unittest.TestCase):
    def test_01_missing_processing_authority_blocks(self):
        case = base_case(); case["processing_authority_documented"] = False
        self.assertEqual(assess_case(case)["primary_outcome"], EV07)

    def test_02_unsafe_input_blocks(self):
        case = base_case(); case["input_safe"] = False
        self.assertEqual(assess_case(case)["primary_outcome"], EV07)

    def test_03_scan_json_agreement_does_not_verify_award(self):
        case = base_case()
        case["field_comparisons"] = [{"field":"award_date", "submitted_value":"2024-01-01", "extracted_value":"2024-01-01"}]
        case["required_claims"] = [claim(scope="individual_award", subject_id="CANDIDATE", predicate="award_confirmed", expected_value="confirmed", relevant_session=None, relevant_date="2024-01-01", required_source_classes=["A"])]
        result = assess_case(case)
        self.assertEqual(result["primary_outcome"], EV05)
        self.assertNotEqual(result["primary_outcome"], EV01)

    def test_04_material_scan_json_mismatch_is_ev06(self):
        case = base_case()
        case["field_comparisons"] = [{"field":"programme", "submitted_value":"BBA", "extracted_value":"BCom"}]
        self.assertEqual(assess_case(case)["primary_outcome"], EV06)

    def test_05_low_confidence_ocr_abstains(self):
        case = base_case()
        case["field_comparisons"] = [{"field":"programme", "submitted_value":"BBA", "extracted_value":"B8A", "ocr_confidence":0.2}]
        self.assertEqual(assess_case(case)["primary_outcome"], EV05)
        self.assertTrue(assess_case(case)["review_required"])

    def test_06_valid_historical_interval_is_consistent(self):
        case = base_case(); case["required_claims"] = [claim()]; case["evidence"] = [evidence()]
        self.assertEqual(assess_case(case)["primary_outcome"], EV01)

    def test_07_current_only_status_without_history_is_insufficient(self):
        case = base_case(); case["required_claims"] = [claim()]
        item = evidence(valid_sessions=["2025-2026"]); item.pop("excluded_sessions", None)
        case["evidence"] = [item]
        self.assertEqual(assess_case(case)["primary_outcome"], EV05)

    def test_08_explicit_non_retroactive_exclusion_is_ev02(self):
        case = base_case(); case["required_claims"] = [claim()]
        case["evidence"] = [evidence(valid_sessions=["2022-2023"], excluded_sessions=["2021-2022"], period_scope_complete=True)]
        self.assertEqual(assess_case(case)["primary_outcome"], EV02)

    def test_09_complete_period_disjoint_from_claim_is_ev02(self):
        case = base_case(); case["required_claims"] = [claim()]
        case["evidence"] = [evidence(valid_sessions=["2022-2023"], period_scope_complete=True)]
        self.assertEqual(assess_case(case)["primary_outcome"], EV02)

    def test_10_unknown_date_precision_is_ev05(self):
        case = base_case(); case["required_claims"] = [claim(relevant_session=None, relevant_date="2021-06-01")]
        case["evidence"] = [evidence(valid_sessions=None, valid_from=None, valid_to=None)]
        self.assertEqual(assess_case(case)["primary_outcome"], EV05)

    def test_11_dependent_sources_share_lineage_group(self):
        case = base_case(); case["evidence"] = [
            evidence(evidence_id="E1", source_id="S1"),
            evidence(evidence_id="E2", source_id="S2", parent_source_id="S1"),
        ]
        groups = assess_case(case)["dependency_groups"]
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["source_ids"], ["S1", "S2"])

    def test_12_unknown_dependency_is_not_assumed_independent_or_dependent(self):
        case = base_case(); case["evidence"] = [
            evidence(evidence_id="E1", source_id="S1"),
            evidence(evidence_id="E2", source_id="S2"),
        ]
        self.assertEqual(assess_case(case)["dependency_groups"], [])

    def test_13_comparable_conflicting_sources_are_ev04(self):
        case = base_case(); case["required_claims"] = [claim()]
        case["evidence"] = [
            evidence(evidence_id="E1", source_id="S1", value="yes"),
            evidence(evidence_id="E2", source_id="S2", value="no"),
        ]
        self.assertEqual(assess_case(case)["primary_outcome"], EV04)

    def test_14_different_periods_do_not_create_conflict(self):
        case = base_case(); case["required_claims"] = [claim()]
        case["evidence"] = [
            evidence(evidence_id="E1", source_id="S1", value="yes", valid_sessions=["2021-2022"]),
            evidence(evidence_id="E2", source_id="S2", value="no", valid_sessions=["2022-2023"]),
        ]
        self.assertNotEqual(assess_case(case)["primary_outcome"], EV04)

    def test_15_affiliation_does_not_establish_individual_award(self):
        case = base_case()
        case["required_claims"] = [
            claim(scope="college_affiliation", subject_id="COLLEGE", predicate="affiliated_with", expected_value="UNI"),
            claim(scope="individual_award", subject_id="CANDIDATE", predicate="award_confirmed", expected_value="confirmed", relevant_session=None, relevant_date="2024-06-01", required_source_classes=["A"]),
        ]
        case["evidence"] = [evidence(claim_scope="college_affiliation", subject_id="COLLEGE", predicate="affiliated_with", value="UNI")]
        result = assess_case(case)
        award = [x for x in result["scope_results"] if x["scope"] == "individual_award"][0]
        self.assertEqual(award["outcome"], EV05)

    def test_16_unresolved_successor_identity_is_ev03(self):
        case = base_case(); case["entity_resolution_status"] = "ambiguous"
        self.assertEqual(assess_case(case)["primary_outcome"], EV03)

    def test_17_null_end_date_is_not_assumed_open_ended(self):
        case = base_case()
        c = claim(relevant_session=None, relevant_date="2022-01-01")
        e = evidence(valid_sessions=None, valid_from="2021-01-01", valid_to=None)
        case["required_claims"] = [c]; case["evidence"] = [e]
        self.assertEqual(assess_case(case)["primary_outcome"], EV05)

    def test_18_contextual_consistency_has_scope_specific_explanation(self):
        case = base_case(); case["required_claims"] = [claim()]; case["evidence"] = [evidence()]
        result = assess_case(case)
        self.assertEqual(result["scope_results"][0]["outcome"], EV01)
        self.assertIn("contextual", result["explanation"].lower())

    def test_19_temporal_mismatch_precedes_award_insufficient(self):
        result = assess_case(get_demo_case("Later-session programme approval"))
        self.assertEqual(result["primary_outcome"], EV02)
        self.assertIn(EV05, result["secondary_findings"])

    def test_20_every_scope_result_has_evidence_or_missing_explanation(self):
        case = base_case(); case["required_claims"] = [claim()]
        result = assess_case(case)
        scope = result["scope_results"][0]
        self.assertTrue(scope["explanation"])
        self.assertIsInstance(scope["evidence_ids"], list)

    def test_21_affiliation_case_returns_entity_ambiguity_primary(self):
        result = assess_case(get_demo_case("Affiliation transition ambiguity"))
        self.assertEqual(result["primary_outcome"], EV03)
        self.assertIn(EV05, result["secondary_findings"])


    def test_23_explicit_in_period_negative_status_is_temporal_mismatch(self):
        case = base_case(); case["required_claims"] = [claim()]
        case["evidence"] = [evidence(value="not_approved", explicitly_excludes_claim=True)]
        self.assertEqual(assess_case(case)["primary_outcome"], EV02)

    def test_22_unverified_award_remains_insufficient_even_when_context_passes(self):
        result = assess_case(get_demo_case("Context supported, award unverified"))
        self.assertEqual(result["primary_outcome"], EV05)
        self.assertEqual(result["scope_results"][0]["outcome"], EV01)
        self.assertEqual(result["scope_results"][-1]["outcome"], EV05)


if __name__ == "__main__":
    unittest.main()
