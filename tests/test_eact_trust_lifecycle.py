import json
import unittest
from pathlib import Path

from eact_trust_lifecycle import (
    build_audit_trail,
    evaluate_trust_lifecycle,
    verify_audit_trail,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_FILE = ROOT / "research" / "EACT_B4_trust_lifecycle_scenarios.json"


def evaluate_case(case):
    return evaluate_trust_lifecycle(
        anchor=case["anchor"],
        lifecycle_events=case["lifecycle_events"],
        verification=case["verification"],
        assessment_time="2026-11-13T00:00:00Z",
    )


class EACTB4ScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with FIXTURE_FILE.open("r", encoding="utf-8") as source:
            cls.scenarios = json.load(source)["scenarios"]

    def test_all_b4_fixtures_match_expected_dispositions(self):
        for case in self.scenarios:
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    evaluate_case(case)["disposition"],
                    case["expected_disposition"],
                )

    def test_routine_rotation_preserves_provable_pre_rotation_signature(self):
        result = evaluate_case(self.scenarios[1])
        self.assertEqual(result["disposition"], "historical_signature_predates_rotation")
        self.assertEqual(result["current_key_state"], "rotated")

    def test_signing_after_rotation_is_not_accepted(self):
        result = evaluate_case(self.scenarios[2])
        self.assertEqual(result["disposition"], "key_rotated_before_signing")
        self.assertEqual(result["historical_key_state_at_signing"], "rotated")

    def test_delayed_compromise_report_is_applied_from_effective_time(self):
        result = evaluate_case(self.scenarios[3])
        codes = {finding["code"] for finding in result["findings"]}
        self.assertEqual(result["disposition"], "key_compromised_at_signing")
        self.assertIn("compromise_reported_after_effective_time", codes)

    def test_trusted_timestamp_before_compromise_supports_historical_ordering(self):
        result = evaluate_case(self.scenarios[4])
        self.assertEqual(result["disposition"], "historical_signature_predates_compromise")
        self.assertEqual(result["historical_key_state_at_signing"], "pre_compromise")

    def test_expired_key_can_be_assessed_for_provable_historical_signature(self):
        result = evaluate_case(self.scenarios[5])
        self.assertEqual(result["disposition"], "historically_valid_key_now_expired")
        self.assertEqual(result["current_key_state"], "expired")

    def test_signature_after_expiry_is_rejected(self):
        result = evaluate_case(self.scenarios[6])
        self.assertEqual(result["disposition"], "key_expired_at_signing")

    def test_unverified_revocation_claim_is_not_applied_as_trusted_event(self):
        result = evaluate_case(self.scenarios[7])
        self.assertEqual(result["disposition"], "lifecycle_event_unverified")
        self.assertEqual(result["current_key_state"], "active")
        self.assertEqual(result["untrusted_event_count"], 1)

    def test_unknown_anchor_is_not_trusted(self):
        result = evaluate_case(self.scenarios[8])
        self.assertEqual(result["disposition"], "trust_anchor_not_established")
        self.assertFalse(result["anchor_trusted"])

    def test_client_clock_cannot_prove_pre_compromise_signing_time(self):
        result = evaluate_case(self.scenarios[9])
        self.assertEqual(result["disposition"], "trusted_signing_time_not_established")
        self.assertFalse(result["timestamp_trusted"])


class AuditTrailTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            {"event_id": "AUD-001", "event": "anchor_registered", "key_id": "KEY-A"},
            {"event_id": "AUD-002", "event": "key_rotated", "key_id": "KEY-A"},
            {"event_id": "AUD-003", "event": "credential_checked", "credential_id": "CRED-1"},
        ]

    def test_generated_audit_chain_verifies(self):
        result = verify_audit_trail(build_audit_trail(self.records))
        self.assertTrue(result["valid"])

    def test_record_tampering_is_detected(self):
        trail = build_audit_trail(self.records)
        trail[1]["record"]["event"] = "key_compromised"
        result = verify_audit_trail(trail)
        self.assertFalse(result["valid"])
        self.assertEqual(result["first_invalid_index"], 2)
        self.assertEqual(result["reason"], "record_hash_mismatch")

    def test_previous_hash_link_tampering_is_detected(self):
        trail = build_audit_trail(self.records)
        trail[2]["previous_hash"] = "f" * 64
        result = verify_audit_trail(trail)
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "previous_hash_mismatch")

    def test_empty_audit_chain_is_valid(self):
        self.assertTrue(verify_audit_trail([])["valid"])

    def test_sequence_tampering_is_detected(self):
        trail = build_audit_trail(self.records)
        trail[0]["sequence"] = 7
        result = verify_audit_trail(trail)
        self.assertEqual(result["reason"], "sequence_mismatch")


if __name__ == "__main__":
    unittest.main()
