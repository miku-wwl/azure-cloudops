"""Tests for the fixed offline AKS readiness fixtures and decision contracts."""
import unittest

from aks_readiness_model import (
    FIXTURE,
    can_evict,
    evaluate_case,
    evaluate_image_pull,
    evaluate_schedule,
    evaluate_workload_identity,
    run_fixtures,
    version_skew_supported,
)
import json


class FixtureTests(unittest.TestCase):
    def test_every_fixture_matches_its_expected_code(self):
        for name, result, expected in run_fixtures():
            with self.subTest(case=name):
                self.assertEqual(result.code, expected)
                self.assertTrue(result.next_check)

    def test_fixture_is_valid_json_and_has_unique_names(self):
        cases = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]
        names = [case["name"] for case in cases]
        self.assertEqual(len(names), len(set(names)))
        self.assertGreaterEqual(len(cases), 7)


class SchedulingTests(unittest.TestCase):
    def setUp(self):
        self.case = next(case for case in json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"] if case["name"] == "pending-compatible-pool-can-scale")

    def test_node_pool_requests_not_instantaneous_cpu_determine_fit(self):
        node = self.case["nodes"][0]
        self.assertFalse(node["cpu_m"] - node["requested_cpu_m"] >= self.case["pod"]["cpu_m"])
        self.assertEqual(evaluate_schedule(self.case).code, "PENDING_SCALE_POSSIBLE")

    def test_pool_max_blocks_an_otherwise_valid_scale_up(self):
        self.case["autoscaler"]["count"] = self.case["autoscaler"]["max"]
        self.assertEqual(evaluate_schedule(self.case).code, "PENDING_MAX_COUNT")

    def test_disabled_autoscaler_does_not_add_capacity(self):
        self.case["autoscaler"]["enabled"] = False
        self.assertEqual(evaluate_schedule(self.case).code, "PENDING_CONSTRAINTS")

    def test_missing_toleration_is_not_fixed_by_raising_max_count(self):
        case = next(case for case in json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"] if case["name"] == "pending-missing-toleration")
        case["autoscaler"]["max"] = 100
        self.assertEqual(evaluate_schedule(case).code, "PENDING_CONSTRAINTS")

    def test_matching_toleration_makes_tainted_node_eligible(self):
        case = next(case for case in json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"] if case["name"] == "pending-missing-toleration")
        case["pod"]["tolerations"] = [{"key": "sku", "operator": "Equal", "value": "gpu", "effect": "NoSchedule"}]
        self.assertEqual(evaluate_schedule(case).code, "SCHEDULED")


class RegistryAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.case = {
            "registry_mode": "RBAC_ONLY",
            "repository": "payments/api",
            "kubelet_identity": "kubelet-01",
            "assigned_identity": "kubelet-01",
            "roles": [{"identity": "kubelet-01", "role": "AcrPull"}],
            "reachable": True,
            "tag_exists": True,
            "architecture_matches": True,
        }

    def test_rbac_only_uses_acrpull_for_the_kubelet_identity(self):
        self.assertEqual(evaluate_image_pull(self.case).code, "IMAGE_PULL_ALLOWED")

    def test_abac_requires_repository_reader_instead_of_acrpull(self):
        self.case["registry_mode"] = "RBAC_ABAC"
        self.assertEqual(evaluate_image_pull(self.case).code, "IMAGE_PULL_AUTH")
        self.case["roles"] = [{"identity": "kubelet-01", "role": "Container Registry Repository Reader"}]
        self.assertEqual(evaluate_image_pull(self.case).code, "IMAGE_PULL_ALLOWED")

    def test_abac_condition_must_match_repository(self):
        self.case["registry_mode"] = "RBAC_ABAC"
        self.case["roles"] = [{"identity": "kubelet-01", "role": "Container Registry Repository Reader", "repository": "shared/other"}]
        self.assertEqual(evaluate_image_pull(self.case).code, "IMAGE_PULL_AUTH")

    def test_workload_identity_does_not_replace_kubelet_pull_identity(self):
        self.case["assigned_identity"] = "pod-workload"
        self.assertEqual(evaluate_image_pull(self.case).code, "IMAGE_PULL_AUTH")

    def test_network_and_image_reference_failures_are_separate_from_auth(self):
        self.case["reachable"] = False
        self.assertEqual(evaluate_image_pull(self.case).code, "IMAGE_PULL_NETWORK")
        self.case["reachable"] = True
        self.case["tag_exists"] = False
        self.assertEqual(evaluate_image_pull(self.case).code, "IMAGE_REFERENCE")

    def test_platform_mismatch_is_not_reported_as_role_failure(self):
        self.case["architecture_matches"] = False
        self.assertEqual(evaluate_image_pull(self.case).code, "IMAGE_PLATFORM")


class WorkloadAndProbeTests(unittest.TestCase):
    def test_federated_identity_requires_exact_issuer_subject_and_audience(self):
        token = {"issuer": "https://issuer/cluster", "subject": "system:serviceaccount:app:api", "audience": "api://AzureADTokenExchange"}
        trust = dict(token)
        self.assertEqual(evaluate_workload_identity(token, trust).code, "FEDERATION_MATCH")
        trust["subject"] = "system:serviceaccount:other:api"
        self.assertEqual(evaluate_workload_identity(token, trust).code, "FEDERATION_MISMATCH")

    def test_startup_probe_gates_liveness_and_readiness(self):
        case = {"startup_succeeded": False, "readiness_succeeded": True, "liveness_succeeded": False}
        from aks_readiness_model import evaluate_probe
        self.assertEqual(evaluate_probe(case).code, "STARTUP_PENDING")

    def test_readiness_failure_removes_eligibility_without_restart(self):
        from aks_readiness_model import evaluate_probe
        case = {"startup_succeeded": True, "readiness_succeeded": False, "liveness_succeeded": True}
        self.assertEqual(evaluate_probe(case).code, "RUNNING_NOT_READY")

    def test_liveness_failure_is_a_restart_condition(self):
        from aks_readiness_model import evaluate_probe
        case = {"startup_succeeded": True, "readiness_succeeded": False, "liveness_succeeded": False}
        self.assertEqual(evaluate_probe(case).code, "CONTAINER_RESTART")


class OperationsTests(unittest.TestCase):
    def test_core_service_and_external_dns_paths_are_distinguished(self):
        from aks_readiness_model import evaluate_dns
        self.assertEqual(evaluate_dns({"query": "api.app.svc.cluster.local", "service_exists": True, "coredns_ready": True}).code, "CLUSTER_SERVICE_RESOLVED")
        self.assertEqual(evaluate_dns({"query": "registry.example.net", "service_exists": False, "coredns_ready": True, "upstream_ready": False}).code, "UPSTREAM_DNS_UNAVAILABLE")

    def test_pdb_blocks_eviction_of_last_minimum_ready_replica(self):
        self.assertFalse(can_evict(1, 1))
        self.assertTrue(can_evict(2, 1))

    def test_negative_replica_counts_are_rejected(self):
        with self.assertRaises(ValueError):
            can_evict(-1, 0)

    def test_current_documented_minor_skew_window_is_enforced(self):
        self.assertTrue(version_skew_supported(30, 28))
        self.assertFalse(version_skew_supported(30, 27))
        self.assertFalse(version_skew_supported(30, 31))


if __name__ == "__main__":
    unittest.main()
