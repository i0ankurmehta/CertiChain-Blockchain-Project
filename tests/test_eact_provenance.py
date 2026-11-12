import json
import unittest
from pathlib import Path

from eact_provenance import (
    DEFAULT_MAX_ISSUER_AUTH_AGE_DAYS,
    DEFAULT_MAX_STATUS_AGE_HOURS,
    evaluate_provenance,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_FILE = ROOT / "research" / "EACT_B3_provenance_scenarios.json"


def evaluate_case(case):
    return evaluate_provenance(
        integrity_result=case["integrity_result"],
        reference_origin=case["reference_origin"],
        reference_signature_status=case["reference_signature_status"],
        issuer_authentication_status=case["issuer_authentication_status"],
        issuer_auth_source=case["issuer_auth_source"],
        issuer_auth_age_days=case["issuer_auth_age_days"],
        credential_status=case["credential_status"],
        status_source_type=case["status_source_type"],
        status_source_authentication=case["status_source_authentication"],
        status_checked_age_hours=case["status_checked_age_hours"],
    )


class EACTB3FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with FIXTURE_FILE.open("r", encoding="utf-8") as source:
            cls.scenarios = json.load(source)["scenarios"]

    def test_all_b3_fixtures_match_predefined_dispositions(self):
        for case in self.scenarios:
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    evaluate_case(case)["disposition"],
                    case["expected_disposition"],
                )

    def test_fresh_authenticated_issuer_revocation_is_confirmed(self):
        result = evaluate_case(self.scenarios[0])
        self.assertEqual(result["disposition"], "credential_status_revoked_confirmed")
        self.assertIn("credential_status_revoked", {f["code"] for f in result["findings"]})

    def test_stale_issuer_authentication_is_not_current(self):
        result = evaluate_case(self.scenarios[1])
        self.assertEqual(result["issuer_freshness"], "stale")
        self.assertIn("issuer_authentication_stale", {f["code"] for f in result["findings"]})

    def test_hash_match_against_unknown_reference_is_not_trusted(self):
        result = evaluate_case(self.scenarios[2])
        self.assertEqual(result["disposition"], "reference_provenance_unverified")
        self.assertFalse(result["reference_trusted"])

    def test_stale_status_snapshot_does_not_confirm_active_status(self):
        result = evaluate_case(self.scenarios[3])
        self.assertEqual(result["status_freshness"], "stale")
        self.assertIn("status_evidence_stale", {f["code"] for f in result["findings"]})

    def test_invalid_reference_signature_blocks_reference_use(self):
        result = evaluate_case(self.scenarios[4])
        self.assertEqual(result["disposition"], "reference_signature_invalid")
        self.assertFalse(result["reference_trusted"])

    def test_untrusted_revoked_claim_is_not_confirmed_revocation(self):
        result = evaluate_case(self.scenarios[5])
        codes = {f["code"] for f in result["findings"]}
        self.assertEqual(result["disposition"], "status_source_untrusted")
        self.assertIn("inactive_status_claim_unconfirmed", codes)
        self.assertNotIn("credential_status_revoked", codes)

    def test_missing_issuer_timestamp_produces_unknown_freshness(self):
        result = evaluate_case(self.scenarios[6])
        self.assertEqual(result["issuer_freshness"], "timestamp_missing")
        self.assertEqual(result["disposition"], "issuer_authentication_timestamp_missing")

    def test_positive_control_passes(self):
        result = evaluate_case(self.scenarios[7])
        self.assertEqual(result["disposition"], "provenance_and_freshness_current")
        self.assertEqual(result["finding_count"], 0)

    def test_trusted_reference_mismatch_is_confirmed(self):
        result = evaluate_case(self.scenarios[8])
        self.assertEqual(result["disposition"], "integrity_mismatch_confirmed")
        self.assertIn("integrity_mismatch_confirmed", {f["code"] for f in result["findings"]})

    def test_both_stale_sources_are_reported(self):
        result = evaluate_case(self.scenarios[9])
        codes = {f["code"] for f in result["findings"]}
        self.assertIn("issuer_authentication_stale", codes)
        self.assertIn("status_evidence_stale", codes)

    def test_freshness_threshold_boundaries_are_inclusive(self):
        result = evaluate_provenance(
            integrity_result="match",
            reference_origin="issuer_signed_manifest",
            reference_signature_status="verified",
            issuer_authentication_status="authenticated",
            issuer_auth_source="trusted_issuer_directory",
            issuer_auth_age_days=DEFAULT_MAX_ISSUER_AUTH_AGE_DAYS,
            credential_status="active",
            status_source_type="issuer_status_api",
            status_source_authentication="authenticated",
            status_checked_age_hours=DEFAULT_MAX_STATUS_AGE_HOURS,
        )
        self.assertEqual(result["issuer_freshness"], "current")
        self.assertEqual(result["status_freshness"], "current")

    def test_negative_age_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_provenance(
                integrity_result="match",
                reference_origin="issuer_signed_manifest",
                reference_signature_status="verified",
                issuer_authentication_status="authenticated",
                issuer_auth_source="trusted_issuer_directory",
                issuer_auth_age_days=-1,
                credential_status="active",
                status_source_type="issuer_status_api",
                status_source_authentication="authenticated",
                status_checked_age_hours=1,
            )

    def test_every_finding_discloses_synthetic_provenance(self):
        result = evaluate_case(self.scenarios[9])
        for finding in result["findings"]:
            self.assertIn("Synthetic/manual", finding["provenance_note"])


if __name__ == "__main__":
    unittest.main()
