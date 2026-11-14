import unittest
from unittest.mock import Mock, patch

from eact_sdjwt import (
    SDJWTError,
    create_sd_jwt_presentation,
    fetch_remote_sd_jwt,
    generate_es256_keypair,
    issue_sd_jwt,
    untrusted_issuer_from_sd_jwt,
    verify_issued_sd_jwt,
    verify_sd_jwt_presentation,
)


class EACTB6SDJWTTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.issuer_keys = generate_es256_keypair()
        cls.holder_keys = generate_es256_keypair()
        cls.claims = {
            "award_status": "awarded",
            "qualification_level": "Bachelor's degree",
            "program_name": "Bachelor of Computer Applications",
            "institution_name": "Northstar Fictional University",
            "cgpa": 8.2,
            "roll_number": "SYN-BCA-001",
        }
        cls.issued = issue_sd_jwt(
            cls.claims,
            issuer="https://issuer.example.edu",
            issuer_private_key_pem=cls.issuer_keys["private_key_pem"],
            holder_public_jwk=cls.holder_keys["public_jwk"],
        )

    def test_issue_select_present_and_verify_only_approved_claims(self):
        issued_check = verify_issued_sd_jwt(
            self.issued["sd_jwt"],
            issuer_public_key=self.issuer_keys["public_jwk"],
            expected_issuer="https://issuer.example.edu",
        )
        self.assertEqual(issued_check["claims"]["cgpa"], 8.2)
        presentation = create_sd_jwt_presentation(
            self.issued,
            selected_claims=["award_status", "qualification_level", "institution_name"],
            holder_private_key_pem=self.holder_keys["private_key_pem"],
            audience="https://verifier.example",
            nonce="nonce-1234567890123456",
        )
        verified = verify_sd_jwt_presentation(
            presentation["presentation"],
            issuer_public_key=self.issuer_keys["public_jwk"],
            expected_issuer="https://issuer.example.edu",
            expected_audience="https://verifier.example",
            expected_nonce="nonce-1234567890123456",
        )
        self.assertEqual(
            set(verified["disclosed_claim_names"]),
            {"award_status", "qualification_level", "institution_name"},
        )
        self.assertNotIn("cgpa", verified["claims"])
        self.assertTrue(verified["key_binding_valid"])

    def test_issuer_signature_tampering_is_rejected(self):
        issued = dict(self.issued)
        token_parts = issued["sd_jwt"].split("~")
        jwt_parts = token_parts[0].split(".")
        signature = jwt_parts[2]
        jwt_parts[2] = ("A" if signature[0] != "A" else "B") + signature[1:]
        token_parts[0] = ".".join(jwt_parts)
        issued["sd_jwt"] = "~".join(token_parts)
        with self.assertRaises(SDJWTError):
            verify_issued_sd_jwt(
                issued["sd_jwt"],
                issuer_public_key=self.issuer_keys["public_jwk"],
                expected_issuer="https://issuer.example.edu",
            )

    def test_wrong_issuer_trust_anchor_is_rejected(self):
        with self.assertRaises(SDJWTError):
            verify_issued_sd_jwt(
                self.issued["sd_jwt"],
                issuer_public_key=self.issuer_keys["public_jwk"],
                expected_issuer="https://other.example.edu",
            )

    def test_wrong_verifier_nonce_is_rejected(self):
        presentation = create_sd_jwt_presentation(
            self.issued,
            selected_claims=["award_status"],
            holder_private_key_pem=self.holder_keys["private_key_pem"],
            audience="https://verifier.example",
            nonce="nonce-correct-1234",
        )
        with self.assertRaises(SDJWTError):
            verify_sd_jwt_presentation(
                presentation["presentation"],
                issuer_public_key=self.issuer_keys["public_jwk"],
                expected_issuer="https://issuer.example.edu",
                expected_audience="https://verifier.example",
                expected_nonce="nonce-replayed-5678",
            )

    def test_wrong_audience_is_rejected(self):
        presentation = create_sd_jwt_presentation(
            self.issued,
            selected_claims=["award_status"],
            holder_private_key_pem=self.holder_keys["private_key_pem"],
            audience="https://verifier.example",
            nonce="nonce-1234567890123456",
        )
        with self.assertRaises(SDJWTError):
            verify_sd_jwt_presentation(
                presentation["presentation"],
                issuer_public_key=self.issuer_keys["public_jwk"],
                expected_issuer="https://issuer.example.edu",
                expected_audience="https://attacker.example",
                expected_nonce="nonce-1234567890123456",
            )

    def test_holder_private_key_must_match_credential_binding(self):
        other_holder = generate_es256_keypair()
        presentation = create_sd_jwt_presentation(
            self.issued,
            selected_claims=["award_status"],
            holder_private_key_pem=other_holder["private_key_pem"],
            audience="https://verifier.example",
            nonce="nonce-1234567890123456",
        )
        with self.assertRaises(SDJWTError):
            verify_sd_jwt_presentation(
                presentation["presentation"],
                issuer_public_key=self.issuer_keys["public_jwk"],
                expected_issuer="https://issuer.example.edu",
                expected_audience="https://verifier.example",
                expected_nonce="nonce-1234567890123456",
            )

    def test_unknown_claim_and_duplicate_claim_selection_rejected(self):
        with self.assertRaises(SDJWTError):
            create_sd_jwt_presentation(
                self.issued,
                selected_claims=["secret_claim"],
                holder_private_key_pem=self.holder_keys["private_key_pem"],
                audience="https://verifier.example",
                nonce="nonce-1234567890123456",
            )
        with self.assertRaises(SDJWTError):
            create_sd_jwt_presentation(
                self.issued,
                selected_claims=["award_status", "award_status"],
                holder_private_key_pem=self.holder_keys["private_key_pem"],
                audience="https://verifier.example",
                nonce="nonce-1234567890123456",
            )

    def test_issuer_identity_extraction_is_untrusted_helper_only(self):
        self.assertEqual(
            untrusted_issuer_from_sd_jwt(self.issued["sd_jwt"]),
            "https://issuer.example.edu",
        )

    def test_reserved_claim_names_rejected_on_issuance(self):
        with self.assertRaises(SDJWTError):
            issue_sd_jwt(
                {"iss": "attacker"},
                issuer="https://issuer.example.edu",
                issuer_private_key_pem=self.issuer_keys["private_key_pem"],
                holder_public_jwk=self.holder_keys["public_jwk"],
            )

    def test_expired_issuer_credential_is_rejected(self):
        expired = issue_sd_jwt(
            self.claims,
            issuer="https://issuer.example.edu",
            issuer_private_key_pem=self.issuer_keys["private_key_pem"],
            holder_public_jwk=self.holder_keys["public_jwk"],
            now=1,
            lifetime_seconds=10,
        )
        with self.assertRaises(SDJWTError):
            verify_issued_sd_jwt(
                expired["sd_jwt"],
                issuer_public_key=self.issuer_keys["public_jwk"],
                expected_issuer="https://issuer.example.edu",
            )

    def test_stale_holder_key_binding_is_rejected(self):
        presentation = create_sd_jwt_presentation(
            self.issued,
            selected_claims=["award_status"],
            holder_private_key_pem=self.holder_keys["private_key_pem"],
            audience="https://verifier.example",
            nonce="nonce-1234567890123456",
            now=1,
        )
        with self.assertRaises(SDJWTError):
            verify_sd_jwt_presentation(
                presentation["presentation"],
                issuer_public_key=self.issuer_keys["public_jwk"],
                expected_issuer="https://issuer.example.edu",
                expected_audience="https://verifier.example",
                expected_nonce="nonce-1234567890123456",
            )

    def test_tampered_disclosure_is_rejected(self):
        presentation = create_sd_jwt_presentation(
            self.issued,
            selected_claims=["award_status"],
            holder_private_key_pem=self.holder_keys["private_key_pem"],
            audience="https://verifier.example",
            nonce="nonce-1234567890123456",
        )
        parts = presentation["presentation"].split("~")
        parts[1] = ("A" if parts[1][0] != "A" else "B") + parts[1][1:]
        tampered = "~".join(parts)
        with self.assertRaises(SDJWTError):
            verify_sd_jwt_presentation(
                tampered,
                issuer_public_key=self.issuer_keys["public_jwk"],
                expected_issuer="https://issuer.example.edu",
                expected_audience="https://verifier.example",
                expected_nonce="nonce-1234567890123456",
            )

    def test_url_connector_requires_https_and_exact_allowlist(self):
        with self.assertRaises(SDJWTError):
            fetch_remote_sd_jwt("http://issuer.example.edu/credential", allowed_hosts={"issuer.example.edu"})
        with self.assertRaises(SDJWTError):
            fetch_remote_sd_jwt("https://attacker.example/credential", allowed_hosts={"issuer.example.edu"})

    @patch("eact_sdjwt.socket.getaddrinfo", return_value=[(None, None, None, None, ("127.0.0.1", 443))])
    def test_url_connector_blocks_private_ip_resolution(self, _mock_dns):
        with self.assertRaises(SDJWTError):
            fetch_remote_sd_jwt("https://issuer.example.edu/credential", allowed_hosts={"issuer.example.edu"})

    @patch("eact_sdjwt.socket.getaddrinfo", return_value=[(None, None, None, None, ("93.184.216.34", 443))])
    @patch("eact_sdjwt.requests.Session")
    def test_allowlisted_online_source_returns_a_retrieval_fingerprint(self, session_factory, _mock_dns):
        response = Mock()
        response.status_code = 200
        response.headers = {"Content-Type": "application/sd-jwt"}
        response.iter_content.return_value = [self.issued["sd_jwt"].encode("ascii")]
        session = session_factory.return_value
        session.get.return_value = response
        result = fetch_remote_sd_jwt(
            "https://issuer.example.edu/credential/123",
            allowed_hosts={"issuer.example.edu"},
        )
        self.assertEqual(result["source_host"], "issuer.example.edu")
        self.assertEqual(result["credential"], self.issued["sd_jwt"])
        self.assertEqual(len(result["sha256"]), 64)
        self.assertEqual(result["http_status"], 200)
        session.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
