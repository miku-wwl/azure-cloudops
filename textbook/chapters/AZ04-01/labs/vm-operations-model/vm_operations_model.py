"""Synthetic VM lifecycle, VMSS rollout, and disk-cap exercise.

This is a deterministic teaching fixture. It does not call or emulate Azure.
"""

from __future__ import annotations

import json
from pathlib import Path


COMPUTE_BILLED_STATES = {"starting", "running", "stopping", "stopped_allocated"}
NO_COMPUTE_BILLED_STATES = {"creating", "deallocating", "stopped_deallocated"}
POWER_STATES = COMPUTE_BILLED_STATES | NO_COMPUTE_BILLED_STATES
PROVISIONING_STATES = {"creating", "updating", "failed", "succeeded", "deleting", "migrating"}
HEALTH_SIGNALS = {"application_health_extension", "load_balancer_probe", "none"}


def interpret_vm_state(power_state: str, provisioning_state: str) -> dict[str, str | bool]:
    if power_state not in POWER_STATES:
        raise ValueError(f"unsupported fixture power state: {power_state}")
    if provisioning_state not in PROVISIONING_STATES:
        raise ValueError(f"unsupported fixture provisioning state: {provisioning_state}")

    compute_billed = power_state in COMPUTE_BILLED_STATES
    if provisioning_state == "failed":
        last_operation = "LAST_CONTROL_PLANE_OPERATION_FAILED"
    elif provisioning_state == "succeeded":
        last_operation = "LAST_CONTROL_PLANE_OPERATION_SUCCEEDED"
    else:
        last_operation = "CONTROL_PLANE_OPERATION_NOT_FINAL"
    resource_cost = (
        "ATTACHED_DISK_NETWORK_COST_MAY_CONTINUE"
        if power_state == "stopped_deallocated"
        else "RESOURCE_COST_REQUIRES_SEPARATE_REVIEW"
    )
    return {
        "power_state": power_state,
        "provisioning_state": provisioning_state,
        "compute_billed": compute_billed,
        "operation_interpretation": last_operation,
        "attached_resource_cost": resource_cost,
        "application_health": "NOT_INFERRED_FROM_CONTROL_PLANE_STATE",
    }


def guest_evidence(ama_installed: bool, dcr_associated: bool, app_health: str = "unknown") -> dict[str, str | bool]:
    if app_health not in {"unknown", "healthy", "unhealthy"}:
        raise ValueError(f"unsupported fixture app health: {app_health}")
    guest_metrics = ama_installed and dcr_associated
    return {
        "host_metrics": "DEFAULT_PLATFORM_HOST_DATA_AVAILABLE",
        "guest_metrics_collected": guest_metrics,
        "guest_interpretation": "GUEST_DATA_CONFIGURED" if guest_metrics else "GUEST_DATA_NOT_PROVEN",
        "application_health": app_health.upper() if guest_metrics else "NOT_INFERRED_FROM_GUEST_COLLECTION",
    }


def evaluate_rollout(
    orchestration: str,
    policy: str,
    model_version: int,
    instance_version: int,
    health_signal: str,
) -> dict[str, str | bool]:
    if orchestration not in {"uniform", "flexible"}:
        raise ValueError(f"unsupported fixture orchestration: {orchestration}")
    if policy not in {"manual", "automatic", "rolling"}:
        raise ValueError(f"unsupported fixture policy: {policy}")
    if model_version < 0 or instance_version < 0:
        raise ValueError("versions must be non-negative")
    if health_signal not in HEALTH_SIGNALS:
        raise ValueError(f"unsupported fixture health signal: {health_signal}")

    if policy == "manual":
        result = "EXISTING_INSTANCE_REMAINS_ON_OLD_MODEL" if instance_version < model_version else "INSTANCE_ALREADY_AT_MODEL"
    elif policy == "automatic":
        result = "AUTOMATIC_ORDER_NOT_GUARANTEED"
    else:
        if orchestration == "flexible":
            has_health = health_signal == "application_health_extension"
        else:
            has_health = health_signal in {"application_health_extension", "load_balancer_probe"}
        result = (
            "ROLLING_BATCHES_USE_HEALTH_SIGNAL"
            if has_health
            else "ROLLING_HEALTH_GATE_CONFIGURATION_REQUIRED"
        )

    return {
        "orchestration": orchestration,
        "policy": policy,
        "result": result,
        "mode_support_recheck": orchestration == "flexible" and policy in {"automatic", "rolling"},
        "scope": "CONCEPTUAL_FIXTURE_ONLY",
    }


def disk_io_ceiling(
    requested_iops: float,
    disk_iops_cap: float,
    vm_iops_cap: float,
    requested_mbps: float,
    disk_mbps_cap: float,
    vm_mbps_cap: float,
    host_cache: str = "none",
) -> dict[str, float | str]:
    if host_cache != "none":
        raise ValueError("fixture models only a single uncached managed-disk path")
    values = (requested_iops, disk_iops_cap, vm_iops_cap, requested_mbps, disk_mbps_cap, vm_mbps_cap)
    if any(value < 0 for value in values):
        raise ValueError("I/O values must be non-negative")

    delivered_iops = min(requested_iops, disk_iops_cap, vm_iops_cap)
    delivered_mbps = min(requested_mbps, disk_mbps_cap, vm_mbps_cap)
    def limiter(request: float, disk_cap: float, vm_cap: float) -> str:
        ceiling = min(disk_cap, vm_cap)
        if request <= ceiling:
            return "DEMAND_BELOW_CONFIGURED_CAPS"
        if disk_cap == vm_cap:
            return "DISK_AND_VM_CAPS_TIE"
        return "DISK_CAP" if disk_cap < vm_cap else "VM_CAP"

    return {
        "delivered_iops": delivered_iops,
        "delivered_mbps": delivered_mbps,
        "iops_limiter": limiter(requested_iops, disk_iops_cap, vm_iops_cap),
        "throughput_limiter": limiter(requested_mbps, disk_mbps_cap, vm_mbps_cap),
    }


def boot_diagnostics_evidence(configured: bool, app_health: str = "unknown") -> dict[str, str | bool]:
    if app_health not in {"unknown", "healthy", "unhealthy"}:
        raise ValueError(f"unsupported fixture app health: {app_health}")
    return {
        "boot_evidence_available": configured,
        "application_health": app_health,
        "conclusion": (
            "BOOT_EVIDENCE_DOES_NOT_PROVE_APP_HEALTH"
            if configured and app_health == "unknown"
            else "BOOT_AND_APP_SIGNALS_REMAIN_SEPARATE"
        ),
    }


def run_fixture(path: Path | None = None) -> list[dict[str, object]]:
    scenario_path = path or Path(__file__).with_name("scenarios").joinpath("vm-operations-cases.json")
    cases = json.loads(scenario_path.read_text(encoding="utf-8"))

    results: list[dict[str, object]] = []
    for case in cases["states"]:
        results.append({"name": case["name"], **interpret_vm_state(case["power_state"], case["provisioning_state"])})
    for case in cases["guest"]:
        results.append({"name": case["name"], **guest_evidence(case["ama_installed"], case["dcr_associated"], case["app_health"])})
    for case in cases["rollouts"]:
        results.append({"name": case["name"], **evaluate_rollout(
            case["orchestration"], case["policy"], case["model_version"],
            case["instance_version"], case["health_signal"]
        )})
    for case in cases["disk"]:
        results.append({"name": case["name"], **disk_io_ceiling(**case["limits"])})
    for case in cases["boot"]:
        results.append({"name": case["name"], **boot_diagnostics_evidence(case["configured"], case["app_health"])})
    return results


def main() -> None:
    for row in run_fixture():
        name = str(row["name"])
        if "compute_billed" in row:
            if row["power_state"] == "running" and row["provisioning_state"] == "failed":
                label = "RUNNING_POWER_WITH_FAILED_CONTROL_OPERATION_APP_UNKNOWN"
            else:
                label = (
                    "COMPUTE_BILLED"
                    if row["compute_billed"]
                    else "COMPUTE_NOT_BILLED_ATTACHED_RESOURCES_MAY_REMAIN"
                )
        elif "guest_metrics_collected" in row:
            label = "HOST_AND_GUEST_EVIDENCE_DIFFER"
        elif "result" in row:
            label = str(row["result"])
        elif "delivered_iops" in row:
            labels = {
                "DISK_CAP": "DISK_LIMITS_IOPS_BEFORE_VM_LIMIT",
                "VM_CAP": "VM_LIMITS_IOPS_BEFORE_DISK_LIMIT",
                "DISK_AND_VM_CAPS_TIE": "DISK_AND_VM_IOPS_LIMITS_TIE",
                "DEMAND_BELOW_CONFIGURED_CAPS": "IOPS_DEMAND_BELOW_CAPS",
            }
            label = labels[row["iops_limiter"]]
        else:
            label = str(row["conclusion"])
        print(f"{name}: {label}")


if __name__ == "__main__":
    main()
