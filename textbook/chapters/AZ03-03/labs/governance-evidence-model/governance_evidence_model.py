"""Synthetic policy, activity-evidence, and Defender boundary model.

This is a teaching fixture only. It does not emulate Azure control planes,
policy evaluation, telemetry, or service billing.
"""

from __future__ import annotations

import json
from pathlib import Path


POLICY_EFFECTS = {"audit", "deny", "deployIfNotExists"}
POLICY_PHASES = {"create", "update", "existing"}


def evaluate_policy(effect: str, condition_matches: bool, phase: str) -> dict[str, str]:
    """Return a deliberately small, documented effect decision."""
    if effect not in POLICY_EFFECTS:
        raise ValueError(f"unsupported fixture effect: {effect}")
    if phase not in POLICY_PHASES:
        raise ValueError(f"unsupported fixture phase: {phase}")

    if not condition_matches:
        request = "NOT_A_REQUEST" if phase == "existing" else "NOT_BLOCKED_BY_THIS_EFFECT"
        return {"request": request, "compliance": "COMPLIANT", "follow_up": "NONE"}

    if effect == "audit":
        return {
            "request": "NOT_A_REQUEST" if phase == "existing" else "NOT_BLOCKED_BY_THIS_EFFECT",
            "compliance": "NON_COMPLIANT",
            "follow_up": "REVIEW_AND_REMEDIATE_BY_CHANGE_PROCESS",
        }

    if effect == "deny":
        return {
            "request": "NON_COMPLIANT_EXISTING_RESOURCE" if phase == "existing" else "BLOCKED_BY_THIS_EFFECT",
            "compliance": "NON_COMPLIANT",
            "follow_up": "REPAIR_EXISTING_RESOURCE" if phase == "existing" else "NONE",
        }

    return {
        "request": "NOT_A_REQUEST" if phase == "existing" else "NOT_BLOCKED_BY_THIS_EFFECT",
        "compliance": "NON_COMPLIANT",
        "follow_up": (
            "REMEDIATION_TASK_REQUIRED"
            if phase == "existing"
            else "POST_SUCCESS_DELAY_AND_IDENTITY_DEPLOYMENT"
        ),
    }


ACTIVITY_EVENTS = {
    "started_management_write": {
        "evidence": "ACTIVITY_LOG_EXPECTED",
        "reason": "A started control-plane write is in the Activity Log boundary.",
    },
    "started_management_action_failure": {
        "evidence": "ACTIVITY_LOG_EXPECTED",
        "reason": "A started control-plane action can record its final failure.",
    },
    "management_read": {
        "evidence": "ACTIVITY_LOG_READ_NOT_TYPICALLY_CAPTURED",
        "reason": "Activity Log does not typically capture read operations.",
    },
    "data_plane_read": {
        "evidence": "RESOURCE_LOGS_REQUIRE_DIAGNOSTIC_SETTING",
        "reason": "Resource logs are service-specific and are not collected by default.",
    },
    "pre_operation_authn_authz_rejection": {
        "evidence": "NO_ACTIVITY_LOG_ENTRY",
        "reason": "ARM rejection before operation start creates no Activity Log entry.",
    },
}


def classify_activity(event_kind: str, diagnostics_enabled: bool = False) -> dict[str, str]:
    if event_kind not in ACTIVITY_EVENTS:
        raise ValueError(f"unsupported fixture event: {event_kind}")
    event = dict(ACTIVITY_EVENTS[event_kind])
    if event_kind == "data_plane_read" and diagnostics_enabled:
        event["evidence"] = "RESOURCE_LOGS_MAY_BE_AVAILABLE"
        event["reason"] = (
            "Configured diagnostic categories may provide resource logs; "
            "the fixture does not promise an event for every operation."
        )
    return event


DEFENDER_ACTIONS = {
    "none": "NO_POLICY_ENFORCEMENT_CONFIGURED",
    "audit": "ASSESSMENT_VIA_AZURE_POLICY_AUDIT",
    "deny": "REQUEST_ENFORCEMENT_VIA_AZURE_POLICY_DENY",
    "enforce": "REMEDIATION_PATH_VIA_AZURE_POLICY_DINE",
}


def evaluate_defender(
    recommendation_present: bool,
    configured_action: str = "none",
    workload_plan_enabled: bool = False,
) -> dict[str, str]:
    if configured_action not in DEFENDER_ACTIONS:
        raise ValueError(f"unsupported fixture action: {configured_action}")

    if not recommendation_present:
        posture = "NO_FIXTURE_RECOMMENDATION"
        enforcement = "NO_POLICY_ENFORCEMENT_CONFIGURED"
    else:
        posture = "RECOMMENDATION_PRESENT"
        enforcement = DEFENDER_ACTIONS[configured_action]

    plan_cost = (
        "PLAN_COST_REQUIRES_CURRENT_PRICE_REVIEW"
        if workload_plan_enabled
        else "NO_WORKLOAD_PLAN_ACTIVATION_IN_FIXTURE"
    )
    return {
        "posture": posture,
        "enforcement": enforcement,
        "workload_plan": plan_cost,
    }


def run_fixture(path: Path | None = None) -> list[dict[str, str]]:
    fixture_path = path or Path(__file__).with_name("scenarios").joinpath("governance-cases.json")
    cases = json.loads(fixture_path.read_text(encoding="utf-8"))
    results: list[dict[str, str]] = []
    for case in cases["policy"]:
        result = evaluate_policy(case["effect"], case["condition_matches"], case["phase"])
        results.append({"name": case["name"], **result})
    for case in cases["activity"]:
        result = classify_activity(case["event_kind"], case.get("diagnostics_enabled", False))
        results.append({"name": case["name"], **result})
    for case in cases["defender"]:
        result = evaluate_defender(
            case["recommendation_present"],
            case.get("configured_action", "none"),
            case.get("workload_plan_enabled", False),
        )
        results.append({"name": case["name"], **result})
    return results


def main() -> None:
    for result in run_fixture():
        if "request" in result:
            if result["request"] == "BLOCKED_BY_THIS_EFFECT":
                status = "BLOCKED_BY_POLICY"
            elif result["follow_up"] == "REMEDIATION_TASK_REQUIRED":
                status = "REMEDIATION_TASK_REQUIRED"
            elif result["compliance"] == "NON_COMPLIANT":
                status = "ALLOWED_NON_COMPLIANT"
            else:
                status = "ALLOWED_COMPLIANT"
        elif "evidence" in result:
            status = result["evidence"]
        else:
            actions = {
                "NO_POLICY_ENFORCEMENT_CONFIGURED": "RECOMMENDATION_ONLY",
                "ASSESSMENT_VIA_AZURE_POLICY_AUDIT": "AUDIT_ONLY",
                "REQUEST_ENFORCEMENT_VIA_AZURE_POLICY_DENY": "REQUEST_ENFORCEMENT_VIA_AZURE_POLICY_DENY",
                "REMEDIATION_PATH_VIA_AZURE_POLICY_DINE": "REMEDIATION_VIA_AZURE_POLICY_DINE",
            }
            status = actions[result["enforcement"]]
        print(f"{result['name']}: {status}")


if __name__ == "__main__":
    main()
