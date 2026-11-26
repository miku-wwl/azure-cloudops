"""Offline AKS readiness decision model; this does not contact Azure or Kubernetes."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

FIXTURE = Path(__file__).parent / "fixtures" / "readiness-cases.json"


@dataclass(frozen=True)
class Evaluation:
    code: str
    next_check: str


def _tolerates(taint: dict[str, str], tolerations: list[dict[str, str]]) -> bool:
    for item in tolerations:
        effect = item.get("effect", "")
        if effect and effect != taint.get("effect", ""):
            continue
        operator = item.get("operator", "Equal")
        if operator == "Exists" and item.get("key", "") in ("", taint.get("key", "")):
            return True
        if (
            operator == "Equal"
            and item.get("key") == taint.get("key")
            and item.get("value", "") == taint.get("value", "")
        ):
            return True
    return False


def _eligible(pod: dict[str, Any], node: dict[str, Any]) -> bool:
    labels = node.get("labels", {})
    if any(labels.get(key) != value for key, value in pod.get("node_selector", {}).items()):
        return False
    for taint in node.get("taints", []):
        if taint.get("effect") in {"NoSchedule", "NoExecute"} and not _tolerates(taint, pod.get("tolerations", [])):
            return False
    return True


def _fits(pod: dict[str, Any], node: dict[str, Any]) -> bool:
    free_cpu = node["cpu_m"] - node.get("requested_cpu_m", 0)
    free_memory = node["memory_mib"] - node.get("requested_memory_mib", 0)
    return pod["cpu_m"] <= free_cpu and pod["memory_mib"] <= free_memory


def evaluate_schedule(case: dict[str, Any]) -> Evaluation:
    pod = case["pod"]
    eligible = [node for node in case.get("nodes", []) if _eligible(pod, node)]
    if any(_fits(pod, node) for node in eligible):
        return Evaluation("SCHEDULED", "Confirm the bound node and continue to kubelet image-pull events.")

    autoscaler = case.get("autoscaler", {})
    template = autoscaler.get("template")
    template_eligible = bool(template and _eligible(pod, template))
    template_fits = bool(template_eligible and _fits(pod, template))
    can_add = autoscaler.get("enabled") and autoscaler.get("count", 0) < autoscaler.get("max", 0)

    if can_add and template_fits:
        return Evaluation("PENDING_SCALE_POSSIBLE", "Check pool limits, quota, regional capacity and subnet IPs.")
    if eligible and autoscaler.get("count", 0) >= autoscaler.get("max", 0):
        return Evaluation("PENDING_MAX_COUNT", "Check max-count and whether a policy-approved capacity change is possible.")
    return Evaluation("PENDING_CONSTRAINTS", "Compare Events, node selector, taints, requests and every eligible pool template.")


def _role_allows(case: dict[str, Any]) -> bool:
    mode = case["registry_mode"]
    expected_role = "AcrPull" if mode == "RBAC_ONLY" else "Container Registry Repository Reader"
    for assignment in case.get("roles", []):
        if assignment.get("identity") != case["kubelet_identity"]:
            continue
        if assignment.get("role") != expected_role:
            continue
        condition_repository = assignment.get("repository")
        if condition_repository is None or condition_repository == case["repository"]:
            return True
    return False


def evaluate_image_pull(case: dict[str, Any]) -> Evaluation:
    if not case.get("reachable", False):
        return Evaluation("IMAGE_PULL_NETWORK", "Check node-to-registry DNS, private endpoint, route, NSG, firewall and TLS/443.")
    if not case.get("tag_exists", False):
        return Evaluation("IMAGE_REFERENCE", "Check registry, repository, tag or digest and manifest availability.")
    if not case.get("architecture_matches", True):
        return Evaluation("IMAGE_PLATFORM", "Compare the image manifest platforms with the selected node architecture.")
    if case.get("assigned_identity") != case.get("kubelet_identity") or not _role_allows(case):
        return Evaluation("IMAGE_PULL_AUTH", "Check the kubelet identity and the role that matches this registry permission mode.")
    return Evaluation("IMAGE_PULL_ALLOWED", "Continue to container startup and probe conditions; pull authorization alone is not readiness.")


def evaluate_workload_identity(token: dict[str, str], trust: dict[str, str]) -> Evaluation:
    keys = ("issuer", "subject", "audience")
    mismatches = [key for key in keys if token.get(key) != trust.get(key)]
    if mismatches:
        return Evaluation("FEDERATION_MISMATCH", "Compare exact issuer, namespace/service-account subject and audience values.")
    return Evaluation("FEDERATION_MATCH", "Then verify target-resource RBAC and application token acquisition.")


def evaluate_probe(case: dict[str, Any]) -> Evaluation:
    if not case.get("startup_succeeded", False):
        return Evaluation("STARTUP_PENDING", "Check startup-probe path, delay, timeout and application initialization.")
    if not case.get("liveness_succeeded", False):
        return Evaluation("CONTAINER_RESTART", "Check process health and liveness logic before changing restart policy.")
    if not case.get("readiness_succeeded", False):
        return Evaluation("RUNNING_NOT_READY", "Inspect readiness and Service endpoints; do not infer liveness failure.")
    return Evaluation("POD_READY", "Check Service selector, EndpointSlice and the actual request path.")


def evaluate_dns(case: dict[str, Any]) -> Evaluation:
    query = case["query"].lower().rstrip(".")
    if not case.get("coredns_ready", False):
        return Evaluation("COREDNS_UNAVAILABLE", "Check CoreDNS pods, Service, events and the Pod resolver configuration.")
    if query.endswith(".svc.cluster.local"):
        if case.get("service_exists", False):
            return Evaluation("CLUSTER_SERVICE_RESOLVED", "Check Service selector, endpoints and network policy for connection failures.")
        return Evaluation("SERVICE_NAME_MISSING", "Check namespace, Service name and search suffix used by the application.")
    if not case.get("upstream_ready", False):
        return Evaluation("UPSTREAM_DNS_UNAVAILABLE", "Check DNS forwarding, VNet resolver and UDP/TCP 53 reachability.")
    return Evaluation("EXTERNAL_DNS_RESOLVED", "Continue with route, TLS and destination authorization checks.")


def can_evict(healthy_replicas: int, min_available: int) -> bool:
    if healthy_replicas < 0 or min_available < 0:
        raise ValueError("replica counts must be non-negative")
    return healthy_replicas - 1 >= min_available


def version_skew_supported(control_plane_minor: int, node_pool_minor: int, max_lag: int = 2) -> bool:
    return 0 <= control_plane_minor - node_pool_minor <= max_lag


def evaluate_case(case: dict[str, Any]) -> Evaluation:
    kind = case["type"]
    if kind == "schedule":
        return evaluate_schedule(case)
    if kind == "image_pull":
        return evaluate_image_pull(case)
    if kind == "probe":
        return evaluate_probe(case)
    if kind == "dns":
        return evaluate_dns(case)
    if kind == "eviction":
        allowed = can_evict(case["healthy_replicas"], case["min_available"])
        return Evaluation("EVICTION_ALLOWED" if allowed else "EVICTION_BLOCKED_BY_PDB", "Recheck Ready replicas and PDB budget before draining.")
    raise ValueError(f"unsupported fixture type: {kind}")


def run_fixtures() -> list[tuple[str, Evaluation, str]]:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return [
        (case["name"], evaluate_case(case), case["expected"])
        for case in payload["cases"]
    ]


if __name__ == "__main__":
    for name, evaluation, expected in run_fixtures():
        status = "PASS" if evaluation.code == expected else "FAIL"
        print(f"{name}: {status} {evaluation.code} | {evaluation.next_check}")
