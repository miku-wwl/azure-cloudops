from __future__ import annotations

import base64
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from token_audience import TokenFormatError, inspect_token  # noqa: E402


def jwt(claims: dict[str, object]) -> str:
    payload = base64.urlsafe_b64encode(json.dumps(claims, separators=(",", ":")).encode()).decode().rstrip("=")
    return f"eyJhbGciOiJub25lIn0.{payload}.synthetic-signature"


class TokenAudienceTests(unittest.TestCase):
    def test_expected_audience_and_allowlisted_claims_are_reported(self) -> None:
        token = jwt({
            "aud": ["https://management.azure.com/", "other"],
            "iss": "https://issuer.example/",
            "tid": "tenant-id",
            "appid": "application-id",
            "scp": "user.read resource.read",
            "roles": ["Reader"],
            "exp": 200,
            "nbf": 100,
            "sub": "subject-value-that-must-not-appear",
            "email": "person@example.test",
            "private_claim": "do-not-copy",
        })
        result = inspect_token(token, "https://management.azure.com/", now=150)
        self.assertTrue(result["audience_match"])
        self.assertEqual(result["scopes"], ["resource.read", "user.read"])
        self.assertEqual(result["roles"], ["Reader"])
        self.assertFalse(result["signature_verified"])
        encoded = json.dumps(result)
        self.assertNotIn("subject-value", encoded)
        self.assertNotIn("person@example", encoded)
        self.assertNotIn("do-not-copy", encoded)

    def test_audience_mismatch_is_explicit(self) -> None:
        self.assertFalse(inspect_token(jwt({"aud": "aud-a"}), "aud-b")["audience_match"])

    def test_expiry_and_not_before_are_labeled_as_unverified_claims(self) -> None:
        result = inspect_token(jwt({"aud": "aud", "exp": 100, "nbf": 200}), now=150)
        self.assertTrue(result["expired_at_inspection_time"])
        self.assertTrue(result["not_yet_valid_at_inspection_time"])
        self.assertIn("untrusted", result["warning"])

    def test_malformed_or_oversized_input_fails_without_echo(self) -> None:
        for token in ("not-a-token", "header.@@@@.signature", "x" * 32769):
            with self.subTest(token_length=len(token)):
                with self.assertRaises(TokenFormatError):
                    inspect_token(token)

    def test_duplicate_json_claim_is_rejected(self) -> None:
        raw = base64.urlsafe_b64encode(b'{"aud":"one","aud":"two"}').decode().rstrip("=")
        with self.assertRaises(TokenFormatError):
            inspect_token(f"header.{raw}.signature")

    def test_unknown_identity_claims_are_not_copied(self) -> None:
        result = inspect_token(jwt({"aud": "aud", "oid": "object-id", "upn": "user@example.test"}))
        self.assertNotIn("oid", result)
        self.assertNotIn("upn", result)


if __name__ == "__main__":
    unittest.main()
