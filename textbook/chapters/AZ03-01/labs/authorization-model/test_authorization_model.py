from __future__ import annotations

import json
import unittest
from pathlib import Path

from authorization_model import AuthorizationModel, FixtureError


FIXTURE = Path(__file__).parent / "scenarios" / "authorization-cases.json"
DOCUMENT = json.loads(FIXTURE.read_text(encoding="utf-8"))
MODEL = AuthorizationModel(DOCUMENT)
REQUESTS = {row["id"]: row for row in DOCUMENT["requests"]}


class TokenBoundaryTests(unittest.TestCase):
    def test_wrong_audience_rejected_before_rbac(self) -> None:
        result = MODEL.evaluate(REQUESTS["wrong-audience"])
        self.assertEqual(("DENY", "TOKEN"), (result.decision, result.stage))
        self.assertIn("audience", result.reason)

    def test_wrong_issuer_rejected(self) -> None:
        request = dict(REQUESTS["data-role-at-child-scope"])
        request["expected_issuer"] = "https://issuer.invalid/tenant"
        result = MODEL.evaluate(request)
        self.assertEqual("TOKEN", result.stage)
        self.assertIn("issuer", result.reason)

    def test_wrong_tenant_rejected_even_with_known_object_id(self) -> None:
        request = dict(REQUESTS["data-role-at-child-scope"])
        request["expected_tenant"] = "22222222-2222-4222-8222-222222222222"
        result = MODEL.evaluate(request)
        self.assertEqual("TOKEN", result.stage)
        self.assertIn("tenant", result.reason)

    def test_fixture_signature_trust_assertion_is_required(self) -> None:
        request = dict(REQUESTS["data-role-at-child-scope"])
        request["signature_trusted"] = False
        result = MODEL.evaluate(request)
        self.assertEqual("TOKEN", result.stage)
        self.assertIn("trust assertion", result.reason)

    def test_expired_token_rejected(self) -> None:
        request = dict(REQUESTS["data-role-at-child-scope"])
        request["token"] = dict(request["token"], exp=request["now"])
        result = MODEL.evaluate(request)
        self.assertEqual("TOKEN", result.stage)
        self.assertIn("expired", result.reason)

    def test_not_yet_valid_token_rejected(self) -> None:
        request = dict(REQUESTS["data-role-at-child-scope"])
        request["token"] = dict(request["token"], nbf=request["now"] + 1)
        result = MODEL.evaluate(request)
        self.assertEqual("TOKEN", result.stage)
        self.assertIn("not yet valid", result.reason)


class RoleAuthorizationTests(unittest.TestCase):
    def test_control_plane_reader_does_not_grant_blob_data(self) -> None:
        result = MODEL.evaluate(REQUESTS["control-reader-is-not-data-reader"])
        self.assertEqual(("DENY", "RBAC"), (result.decision, result.stage))
        self.assertIn("assignments matched", result.reason)

    def test_child_assignment_grants_only_its_scope(self) -> None:
        allowed = MODEL.evaluate(REQUESTS["data-role-at-child-scope"])
        sibling = MODEL.evaluate(REQUESTS["sibling-scope-is-not-inherited"])
        self.assertEqual("ALLOW", allowed.decision)
        self.assertEqual(("DENY", "RBAC"), (sibling.decision, sibling.stage))

    def test_parent_scope_data_assignment_is_inherited(self) -> None:
        result = MODEL.evaluate(REQUESTS["parent-scope-inherits-to-child"])
        self.assertEqual("ALLOW", result.decision)
        self.assertEqual(("a-inherited-data-reader",), result.assignments)

    def test_control_action_inherits_from_resource_group(self) -> None:
        request = dict(REQUESTS["control-reader-is-not-data-reader"])
        request["plane"] = "control"
        request["operation"] = "Microsoft.Storage/storageAccounts/read"
        result = MODEL.evaluate(request)
        self.assertEqual("ALLOW", result.decision)
        self.assertEqual(("a-control-reader",), result.assignments)

    def test_token_scp_or_roles_claim_is_not_a_rbac_assignment(self) -> None:
        request = dict(REQUESTS["control-reader-is-not-data-reader"])
        request["token"] = dict(request["token"], roles=["Storage Blob Data Owner"])
        result = MODEL.evaluate(request)
        self.assertEqual("DENY", result.decision)

    def test_not_data_actions_subtraction_does_not_override_second_role(self) -> None:
        result = MODEL.evaluate(REQUESTS["not-data-actions-is-not-a-deny-assignment"])
        self.assertEqual("ALLOW", result.decision)
        self.assertEqual(("a-second-delete-grant",), result.assignments)

    def test_matching_not_actions_remove_grant_in_that_role(self) -> None:
        request = dict(REQUESTS["data-role-at-child-scope"])
        request["token"] = dict(
            request["token"], oid="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
        )
        request["expected_audience"] = "https://management.azure.com/"
        request["token"] = dict(request["token"], aud="https://management.azure.com/")
        request["plane"] = "control"
        request["operation"] = "Microsoft.Authorization/roleAssignments/write"
        request["target"] = "sa-ledger"
        result = MODEL.evaluate(request)
        self.assertEqual("DENY", result.decision)
        self.assertIn("NotActions", result.reason)

    def test_assignment_identity_includes_tenant_and_object_id(self) -> None:
        request = dict(REQUESTS["data-role-at-child-scope"])
        request["token"] = dict(
            request["token"], tid="22222222-2222-4222-8222-222222222222"
        )
        request["expected_tenant"] = request["token"]["tid"]
        request["expected_issuer"] = (
            "https://login.microsoftonline.com/22222222-2222-4222-8222-222222222222/v2.0"
        )
        request["token"] = dict(request["token"], iss=request["expected_issuer"])
        result = MODEL.evaluate(request)
        self.assertEqual(("DENY", "RBAC"), (result.decision, result.stage))


class FixtureValidationTests(unittest.TestCase):
    def test_unknown_target_is_reported(self) -> None:
        request = dict(REQUESTS["data-role-at-child-scope"], target="unknown")
        with self.assertRaisesRegex(FixtureError, "unknown target scope"):
            MODEL.evaluate(request)

    def test_scope_cycle_is_rejected(self) -> None:
        document = dict(DOCUMENT)
        document["scopes"] = [
            {"id": "a", "parent": "b"},
            {"id": "b", "parent": "a"},
        ]
        document["roles"] = []
        document["assignments"] = []
        with self.assertRaisesRegex(FixtureError, "cycle"):
            AuthorizationModel(document)

    def test_unknown_assignment_role_is_rejected(self) -> None:
        document = json.loads(json.dumps(DOCUMENT))
        document["assignments"][0]["role_id"] = "missing-role"
        with self.assertRaisesRegex(FixtureError, "unknown role"):
            AuthorizationModel(document)


if __name__ == "__main__":
    unittest.main()
