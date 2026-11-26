from __future__ import annotations

import json
import unittest
from pathlib import Path

from credential_flow_model import CredentialFlowModel, FixtureError


FIXTURE = Path(__file__).parent / "scenarios" / "credential-flow-cases.json"
DOCUMENT = json.loads(FIXTURE.read_text(encoding="utf-8"))
MODEL = CredentialFlowModel(DOCUMENT)
REQUESTS = {row["id"]: row for row in DOCUMENT["requests"]}


class ManagedIdentitySelectionTests(unittest.TestCase):
    def test_explicit_user_assigned_identity_can_read(self) -> None:
        result = MODEL.evaluate(REQUESTS["managed-identity-secret-read"])
        self.assertEqual(("ALLOW", "COMPLETE"), (result.decision, result.stage))
        self.assertEqual("uami-settlement", result.identity_id)

    def test_omitted_selector_defaults_to_system_identity_when_present(self) -> None:
        request = dict(REQUESTS["managed-identity-secret-read"])
        request["host_id"] = "app-settlement"
        request["identity_selector"] = None
        request["entra_access_token"] = dict(
            request["entra_access_token"], principal_id="principal-system-settlement"
        )
        result = MODEL.evaluate(request)
        self.assertEqual("mi-system-settlement", result.identity_id)
        self.assertEqual("AUTHZ", result.stage)

    def test_multiple_user_assigned_identities_require_selector(self) -> None:
        result = MODEL.evaluate(REQUESTS["multiple-identities-require-selector"])
        self.assertEqual(("DENY", "CREDENTIAL"), (result.decision, result.stage))

    def test_unattached_identity_is_rejected(self) -> None:
        request = dict(REQUESTS["managed-identity-secret-read"], identity_selector="uami-ci")
        result = MODEL.evaluate(request)
        self.assertEqual(("DENY", "CREDENTIAL"), (result.decision, result.stage))


class WorkloadFederationTests(unittest.TestCase):
    def test_exact_external_claims_exchange_to_configured_identity(self) -> None:
        result = MODEL.evaluate(REQUESTS["federated-workload-secret-read"])
        self.assertEqual(("ALLOW", "COMPLETE"), (result.decision, result.stage))
        self.assertEqual("uami-ci", result.identity_id)

    def test_federated_subject_match_is_case_sensitive(self) -> None:
        request = dict(REQUESTS["federated-workload-secret-read"])
        request["external_token"] = dict(request["external_token"], sub="repo:Contoso/ledger:ref:refs/heads/main")
        result = MODEL.evaluate(request)
        self.assertEqual(("DENY", "FEDERATION"), (result.decision, result.stage))

    def test_wrong_incoming_audience_blocks_exchange(self) -> None:
        request = dict(REQUESTS["federated-workload-secret-read"])
        request["external_token"] = dict(request["external_token"], aud="https://vault.azure.net")
        result = MODEL.evaluate(request)
        self.assertEqual("FEDERATION", result.stage)

    def test_external_exchange_audience_is_not_final_key_vault_audience(self) -> None:
        request = dict(REQUESTS["federated-workload-secret-read"])
        request["entra_access_token"] = dict(
            request["entra_access_token"], aud="api://AzureADTokenExchange"
        )
        result = MODEL.evaluate(request)
        self.assertEqual(("DENY", "TOKEN"), (result.decision, result.stage))


class KeyVaultGateTests(unittest.TestCase):
    def test_key_vault_contributor_does_not_grant_secret_read(self) -> None:
        result = MODEL.evaluate(REQUESTS["contributor-is-control-plane-only"])
        self.assertEqual(("DENY", "AUTHZ"), (result.decision, result.stage))

    def test_network_gate_is_independent_of_identity_and_role(self) -> None:
        result = MODEL.evaluate(REQUESTS["network-blocks-authorized-identity"])
        self.assertEqual(("DENY", "NETWORK"), (result.decision, result.stage))

    def test_wrong_key_vault_audience_is_rejected_before_network(self) -> None:
        result = MODEL.evaluate(REQUESTS["wrong-final-token-audience"])
        self.assertEqual(("DENY", "TOKEN"), (result.decision, result.stage))

    def test_legacy_access_policy_is_used_only_in_legacy_mode(self) -> None:
        allowed = MODEL.evaluate(REQUESTS["legacy-access-policy-secret-read"])
        self.assertEqual(("ALLOW", "COMPLETE"), (allowed.decision, allowed.stage))
        request = dict(REQUESTS["legacy-access-policy-secret-read"], vault_id="vault-rbac-no-role")
        result = MODEL.evaluate(request)
        self.assertEqual("AUTHZ", result.stage)

    def test_missing_data_role_is_not_fixed_by_a_valid_token(self) -> None:
        result = MODEL.evaluate(REQUESTS["valid-token-without-data-role"])
        self.assertEqual(("DENY", "AUTHZ"), (result.decision, result.stage))

    def test_wrong_principal_token_cannot_use_selected_identity_role(self) -> None:
        request = dict(REQUESTS["managed-identity-secret-read"])
        request["entra_access_token"] = dict(
            request["entra_access_token"], principal_id="principal-someone-else"
        )
        result = MODEL.evaluate(request)
        self.assertEqual("TOKEN", result.stage)
        self.assertIn("principal", result.reason)


class FixtureValidationTests(unittest.TestCase):
    def test_duplicate_host_attachment_is_rejected(self) -> None:
        document = json.loads(json.dumps(DOCUMENT))
        document["hosts"][0]["user_assigned"].append("uami-settlement")
        with self.assertRaisesRegex(FixtureError, "more than once"):
            CredentialFlowModel(document)

    def test_unknown_symbolic_role_is_rejected(self) -> None:
        document = json.loads(json.dumps(DOCUMENT))
        document["vaults"][0]["role_assignments"][0]["role"] = "Unknown Role"
        request = next(row for row in document["requests"] if row["vault_id"] == document["vaults"][0]["id"])
        model = CredentialFlowModel(document)
        with self.assertRaisesRegex(FixtureError, "unknown symbolic role"):
            model.evaluate(request)


if __name__ == "__main__":
    unittest.main()
