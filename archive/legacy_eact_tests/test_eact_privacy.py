import copy
import json
import unittest
from pathlib import Path

from eact_privacy import (
    CLAIM_CATALOG,
    evaluate_disclosure_request,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_FILE = ROOT / "research" / "EACT_B5_privacy_scenarios.json"


def load_scenarios():
    with FIXTURE_FILE.open("r", encoding="utf-8") as source:
        return json.load(source)["scenarios"]


class EACTB5FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenarios = load_scenarios()
        cls.by_id = {case["id"]: case for case in cls.scenarios}

    def test_all_b5_fixtures_match_expected_dispositions(self):
        for case in self.scenarios:
            with self.subTest(case=case["id"]):
                result = evaluate_disclosure_request(case)
                self.assertEqual(result["disposition"], case["expected_disposition"])

    def test_positive_control_discloses_only_minimum_degree_claims(self):
        result = evaluate_disclosure_request(self.by_id["B5-01"])
        self.assertTrue(result["can_verify_purpose"])
        self.assertTrue(result["presentation_ready"])
        self.assertEqual(
            set(result["proposed_claims"]),
            {"award_status", "qualification_level", "program_name", "institution_name"},
        )
        self.assertEqual(result["additional_proposed_claims"], [])

    def test_full_record_request_flags_excessive_and_sensitive_disclosure(self):
        result = evaluate_disclosure_request(self.by_id["B5-02"])
        codes = {item["code"] for item in result["findings"]}
        self.assertTrue(result["can_verify_purpose"])
        self.assertFalse(result["presentation_ready"])
        self.assertIn("request_exceeds_purpose", codes)
        self.assertIn("high_sensitivity_claims_proposed", codes)
        self.assertGreater(result["proposed_claim_count"], len(result["minimum_required_claims"]))

    def test_threshold_predicate_does_not_reveal_raw_cgpa(self):
        result = evaluate_disclosure_request(self.by_id["B5-03"])
        self.assertEqual(result["disposition"], "minimum_disclosure_sufficient")
        self.assertNotIn("cgpa", result["proposed_claims"])
        self.assertEqual(result["predicate_results"][0]["satisfied"], True)
        self.assertTrue(result["can_verify_purpose"])

    def test_failed_threshold_returns_predicate_result_without_raw_score(self):
        case = copy.deepcopy(self.by_id["B5-03"])
        case["credential"]["claims"]["cgpa"] = 6.8
        result = evaluate_disclosure_request(case)
        self.assertEqual(result["disposition"], "insufficient_evidence_or_consent")
        self.assertEqual(result["predicate_results"][0]["satisfied"], False)
        self.assertNotIn("cgpa", result["proposed_claims"])

    def test_internship_policy_uses_enrollment_not_transcript(self):
        result = evaluate_disclosure_request(self.by_id["B5-04"])
        self.assertEqual(
            set(result["proposed_claims"]),
            {"enrollment_status", "program_name", "institution_name"},
        )
        self.assertNotIn("transcript", result["proposed_claims"])

    def test_required_claim_withheld_by_holder_blocks_completion(self):
        result = evaluate_disclosure_request(self.by_id["B5-05"])
        self.assertFalse(result["can_verify_purpose"])
        self.assertEqual(result["disposition"], "insufficient_evidence_or_consent")
        self.assertIn("institution_name", result["missing_required_claims"])

    def test_unknown_purpose_fails_closed_without_proposed_claims(self):
        result = evaluate_disclosure_request(self.by_id["B5-06"])
        self.assertEqual(result["disposition"], "purpose_not_supported")
        self.assertEqual(result["proposed_claims"], {})
        self.assertFalse(result["can_verify_purpose"])

    def test_global_identifier_is_flagged_even_when_consent_is_given(self):
        result = evaluate_disclosure_request(self.by_id["B5-07"])
        codes = {item["code"] for item in result["findings"]}
        self.assertIn("persistent_identifier_shared", codes)
        self.assertIn("global_student_id", result["proposed_claims"])

    def test_cross_verifier_use_of_global_identifier_is_detected(self):
        result = evaluate_disclosure_request(self.by_id["B5-08"])
        codes = {item["code"] for item in result["findings"]}
        self.assertIn("cross_verifier_linkability", codes)

    def test_quasi_identifier_combination_is_flagged(self):
        result = evaluate_disclosure_request(self.by_id["B5-09"])
        codes = {item["code"] for item in result["findings"]}
        self.assertIn("quasi_identifier_combination", codes)

    def test_secondary_use_requires_review_and_retention_is_flagged(self):
        result = evaluate_disclosure_request(self.by_id["B5-10"])
        codes = {item["code"] for item in result["findings"]}
        self.assertEqual(result["disposition"], "secondary_use_requires_review")
        self.assertIn("secondary_use_mismatch", codes)
        self.assertIn("retention_not_specified", codes)
        self.assertFalse(result["can_verify_purpose"])

    def test_untrusted_issuer_blocks_any_presentation_proposal(self):
        result = evaluate_disclosure_request(
            self.by_id["B5-01"], issuer_trust="unknown"
        )
        self.assertEqual(result["disposition"], "issuer_trust_not_established")
        self.assertEqual(result["proposed_claims"], {})

    def test_non_active_credential_status_blocks_presentation(self):
        result = evaluate_disclosure_request(
            self.by_id["B5-01"], credential_status="revoked"
        )
        self.assertEqual(result["disposition"], "credential_status_not_active")
        self.assertEqual(result["proposed_claims"], {})

    def test_approved_but_unrequested_claim_is_not_disclosed(self):
        result = evaluate_disclosure_request(
            self.by_id["B5-01"],
            approved_claims=[
                "award_status", "qualification_level", "program_name",
                "institution_name", "date_of_birth",
            ],
        )
        self.assertNotIn("date_of_birth", result["proposed_claims"])

    def test_extra_requested_but_not_approved_claim_is_not_disclosed(self):
        result = evaluate_disclosure_request(
            self.by_id["B5-02"],
            approved_claims=[
                "award_status", "qualification_level", "program_name", "institution_name"
            ],
        )
        self.assertTrue(result["can_verify_purpose"])
        self.assertNotIn("transcript", result["proposed_claims"])
        self.assertIn("transcript", result["not_approved_claims"])

    def test_unknown_claim_name_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_disclosure_request(
                self.by_id["B5-01"],
                requested_claims=["award_status", "secret_internal_field"],
            )

    def test_disclosure_exposure_is_lower_than_full_record_baseline(self):
        result = evaluate_disclosure_request(self.by_id["B5-01"])
        self.assertLess(
            result["proposed_exposure_units"],
            result["full_credential_exposure_units"],
        )
        self.assertGreater(result["exposure_reduction_percent"], 0.0)

    def test_claim_catalog_contains_only_known_synthetic_attributes(self):
        result = evaluate_disclosure_request(self.by_id["B5-01"])
        self.assertEqual(
            set(result["proposed_claims"]),
            set(result["minimum_required_claims"]),
        )
        self.assertTrue(set(result["proposed_claims"]).issubset(CLAIM_CATALOG))


if __name__ == "__main__":
    unittest.main()
