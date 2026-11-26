import json
import unittest
from pathlib import Path

from scope_model import ScopeError, ScopeModel

SCENARIO = Path(__file__).parent / "scenarios" / "banking-lz.json"


class ScopeModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(SCENARIO.read_text(encoding="utf-8"))
        cls.model = ScopeModel(cls.document)

    def test_management_group_grant_inherits_into_workload_subscription(self):
        self.assertTrue(
            self.model.allows(
                "platform-auditors",
                "storage-prod",
                "Microsoft.Resources/subscriptions/read",
                "control",
            )
        )

    def test_resource_group_grant_reaches_child_resource(self):
        self.assertTrue(
            self.model.allows(
                "dev-operators",
                "storage-dev",
                "Microsoft.Network/virtualNetworks/write",
                "control",
            )
        )

    def test_resource_group_grant_does_not_cross_to_sibling_subscription(self):
        self.assertFalse(
            self.model.allows(
                "dev-operators",
                "storage-prod",
                "Microsoft.Network/virtualNetworks/write",
                "control",
            )
        )

    def test_data_action_does_not_grant_control_plane_action(self):
        self.assertTrue(
            self.model.allows(
                "dev-operators",
                "storage-dev",
                "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/read",
                "data",
            )
        )
        self.assertFalse(
            self.model.allows(
                "dev-operators",
                "storage-dev",
                "Microsoft.Storage/storageAccounts/write",
                "control",
            )
        )

    def test_plane_argument_must_be_explicit(self):
        with self.assertRaises(ValueError):
            self.model.allows("dev-operators", "storage-dev", "*", "both")

    def test_unknown_scope_is_not_silently_treated_as_root(self):
        with self.assertRaises(ScopeError):
            self.model.scope_chain("missing")

    def test_parent_cycle_is_detected(self):
        cyclic = {
            "scopes": [
                {"id": "a", "arm_scope": "/a", "parent": "b"},
                {"id": "b", "arm_scope": "/b", "parent": "a"},
            ],
            "assignments": [],
        }
        with self.assertRaises(ScopeError):
            ScopeModel(cyclic)


if __name__ == "__main__":
    unittest.main()
