import json
import unittest
from pathlib import Path

from eact_rules import evaluate_evidence, hash_only_baseline


ROOT = Path(__file__).resolve().parents[1]
SCENARIO_FILE = ROOT / "research" / "verification_scenarios.json"


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
                self.assertEqual(
                    result["disposition"], scenario["expected_disposition"]
                )

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


if __name__ == "__main__":
    unittest.main()
