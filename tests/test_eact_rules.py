import json
import unittest
from pathlib import Path

from eact_rules import (
    evaluate_evidence,
    evaluate_evidence_v2,
    hash_only_baseline,
)


ROOT = Path(__file__).resolve().parents[1]
SCENARIO_FILE = ROOT / "research" / "verification_scenarios.json"
B2_FILE = ROOT / "research" / "EACT_B2_conflict_scenarios.json"


class EACTScenarioConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with SCENARIO_FILE.open("r", encoding="utf-8") as source:
            cls.scenarios = json.load(source)["scenarios"]

    def test_all_fictional_scenarios_match_predefined_expected_disposition(self):
        for scenario in self.scenarios:
            with self.subTest(scenario=scenario["id"]):
                result = evaluate_evidence(
                    integrity=scenario["integrity"],
                    issuer_identity=scenario["issuer_identity"],
                    credential_status=scenario["credential_status"],
                    subject_match=scenario["subject_match"],
                    source_state=scenario["source_state"],
                )
                self.assertEqual(result["disposition"], scenario["expected_disposition"])

    def test_hash_match_does_not_equal_authenticity(self):
        baseline = hash_only_baseline("match")
        eact = evaluate_evidence(
            integrity="match",
            issuer_identity="unknown",
            credential_status="unknown",
            subject_match="not_checked",
            source_state="offline_document_only",
        )
        self.assertEqual(baseline["disposition"], "valid")
        self.assertEqual(eact["disposition"], "issuer_unverified")

    def test_source_unavailable_is_not_fraud(self):
        result = evaluate_evidence(
            integrity="match",
            issuer_identity="unknown",
            credential_status="unknown",
            subject_match="match",
            source_state="service_unavailable",
        )
        self.assertEqual(result["disposition"], "inconclusive_source_unavailable")

    def test_pending_consent_is_not_fraud(self):
        result = evaluate_evidence(
            integrity="not_checked",
            issuer_identity="unknown",
            credential_status="unknown",
            subject_match="not_checked",
            source_state="consent_pending",
        )
        self.assertEqual(result["disposition"], "pending_consent")

    def test_integrity_mismatch_is_reported_as_altered(self):
        result = evaluate_evidence(
            integrity="mismatch",
            issuer_identity="authenticated",
            credential_status="active",
            subject_match="match",
            source_state="available",
        )
        self.assertEqual(result["disposition"], "altered")


class EACTv2MultiFindingTests(unittest.TestCase):
    def test_revoked_and_subject_mismatch_are_both_reported(self):
        result = evaluate_evidence_v2(
            integrity="match",
            issuer_identity="authenticated",
            credential_status="revoked",
            subject_match="mismatch",
            source_state="status_source_available",
        )
        codes = {finding["code"] for finding in result["findings"]}
        self.assertEqual(result["disposition"], "manual_review_multiple_findings")
        self.assertIn("credential_revoked", codes)
        self.assertIn("subject_mismatch", codes)

    def test_unknown_issuer_does_not_authenticate_status_claim(self):
        result = evaluate_evidence_v2(
            integrity="match",
            issuer_identity="unknown",
            credential_status="revoked",
            subject_match="mismatch",
            source_state="status_source_available",
        )
        codes = {finding["code"] for finding in result["findings"]}
        self.assertEqual(result["disposition"], "issuer_unverified")
        self.assertIn("issuer_not_authenticated", codes)
        self.assertIn("status_claim_not_authenticated", codes)
        self.assertIn("subject_mismatch", codes)

    def test_integrity_mismatch_and_source_outage_are_both_visible(self):
        result = evaluate_evidence_v2(
            integrity="mismatch",
            issuer_identity="unknown",
            credential_status="unknown",
            subject_match="not_checked",
            source_state="service_unavailable",
        )
        codes = {finding["code"] for finding in result["findings"]}
        self.assertEqual(result["disposition"], "altered")
        self.assertIn("integrity_mismatch", codes)
        self.assertIn("verification_source_unavailable", codes)

    def test_status_unknown_partial_verification_is_preserved(self):
        result = evaluate_evidence_v2(
            integrity="match",
            issuer_identity="authenticated",
            credential_status="unknown",
            subject_match="match",
            source_state="status_service_unavailable",
        )
        self.assertEqual(
            result["disposition"],
            "issuer_and_integrity_verified_status_unknown",
        )
        self.assertIn(
            "verification_source_unavailable",
            {finding["code"] for finding in result["findings"]},
        )
        self.assertIn(
            "credential_status_unknown",
            {finding["code"] for finding in result["findings"]},
        )

    def test_clean_scenario_has_no_adverse_findings(self):
        result = evaluate_evidence_v2(
            integrity="match",
            issuer_identity="authenticated",
            credential_status="active",
            subject_match="match",
            source_state="available_consent_granted",
        )
        self.assertEqual(result["disposition"], "verified_against_trusted_source")
        self.assertEqual(result["finding_count"], 0)

    def test_every_finding_discloses_synthetic_input_provenance(self):
        result = evaluate_evidence_v2(
            integrity="match",
            issuer_identity="unknown",
            credential_status="revoked",
            subject_match="mismatch",
            source_state="status_source_available",
        )
        for finding in result["findings"]:
            self.assertIn("Synthetic/manual", finding["provenance"])


if __name__ == "__main__":
    unittest.main()
