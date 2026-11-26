"""Synthetic App Service slot and Container Apps release model.

This fixture does not call Azure APIs and is not an Azure service emulator.
"""
from __future__ import annotations

import json
from pathlib import Path

REVISION_SCOPE = {"image", "container", "probe", "scale"}
APP_SCOPE = {"secret", "ingress", "traffic", "revision_mode", "identity", "registry", "dapr"}


def warmup_accepted(status_code: int | None, accepted_statuses: list[int] | None = None) -> bool:
    """Model documented warm-up behavior; None means no HTTP response."""
    if status_code is None or not 100 <= status_code <= 599:
        return False
    return accepted_statuses is None or status_code in accepted_statuses


def swap_slots(production: dict, staging: dict, status_code: int | None,
               accepted_statuses: list[int] | None = None, restart_ok: bool = True) -> dict:
    """Model a successful route swap while identity stays associated with its slot."""
    if not restart_ok or not warmup_accepted(status_code, accepted_statuses):
        return {
            "completed": False,
            "production": production["release"],
            "staging": staging["release"],
            "production_identity": production["identity"],
            "staging_identity": staging["identity"],
        }
    return {
        "completed": True,
        "production": staging["release"],
        "staging": production["release"],
        "production_identity": production["identity"],
        "staging_identity": staging["identity"],
    }


def classify_changes(changes: list[str]) -> dict:
    """Return simplified documented scopes; reject unclassified properties."""
    unknown = sorted(set(changes) - REVISION_SCOPE - APP_SCOPE)
    if unknown:
        raise ValueError(f"unknown change type(s): {', '.join(unknown)}")
    return {
        "revision_created": bool(set(changes) & REVISION_SCOPE),
        "app_scope_changed": bool(set(changes) & APP_SCOPE),
        "secret_restart_required": "secret" in changes,
        "identity_restart_automatic": False if "identity" in changes else None,
    }


def _valid_weights(weights: dict[str, int]) -> bool:
    return bool(weights) and all(0 <= value <= 100 for value in weights.values()) and sum(weights.values()) == 100


def plan_cutover(mode: str, current_revision: str, candidate_revision: str,
                 ready: bool, weights: dict[str, int] | None = None) -> dict:
    """Apply a local release policy around documented single/multiple modes."""
    if mode == "single":
        return {
            "allowed": True,
            "traffic": ({candidate_revision: 100} if ready else {current_revision: 100}),
            "reason": "ready" if ready else "candidate_not_ready_keep_current",
        }
    if mode != "multiple":
        raise ValueError("mode must be 'single' or 'multiple'")
    weights = weights or {current_revision: 100, candidate_revision: 0}
    if not _valid_weights(weights):
        raise ValueError("multiple-revision traffic weights must be nonnegative and total 100")
    if weights.get(candidate_revision, 0) > 0 and not ready:
        return {"allowed": False, "traffic": weights, "reason": "release_policy_requires_readiness"}
    return {"allowed": True, "traffic": weights, "reason": "ready" if ready else "no_candidate_traffic"}


def rollback_route(previous_revision: str, candidate_revision: str, previous_is_active: bool) -> dict:
    """Model traffic rollback only; it intentionally leaves app-wide config untouched."""
    if not previous_is_active:
        return {"allowed": False, "reason": "previous_revision_not_active_redeploy_required"}
    return {"allowed": True, "traffic": {previous_revision: 100, candidate_revision: 0},
            "app_scope_changed": False}


def _run_case(case: dict) -> str:
    kind = case["kind"]
    if kind == "warmup":
        accepted = warmup_accepted(case.get("status"), case.get("accepted_statuses"))
        return "WARMUP_ACCEPTED" if accepted else "WARMUP_REJECTED"
    if kind == "swap":
        result = swap_slots(case["production"], case["staging"], case.get("status"),
                            case.get("accepted_statuses"), case.get("restart_ok", True))
        if not result["completed"]:
            return "SWAP_BLOCKED"
        return (f"PROD={result['production']} STAGING={result['staging']} "
                f"IDENTITIES={result['production_identity']},{result['staging_identity']}")
    if kind == "single_cutover":
        result = plan_cutover("single", case["current"], case["candidate"], case["ready"])
        route = next(iter(result["traffic"].items()))
        return f"PROD_TRAFFIC={route[0]}:{route[1]}"
    if kind == "multiple_cutover":
        result = plan_cutover("multiple", case["current"], case["candidate"],
                              case["ready"], case["weights"])
        if not result["allowed"]:
            return f"CUTOVER_BLOCKED={result['reason']}"
        route = ",".join(f"{revision}:{weight}" for revision, weight in result["traffic"].items())
        return f"TRAFFIC={route} SUM={sum(result['traffic'].values())}"
    if kind == "rollback":
        result = rollback_route(case["previous"], case["candidate"], case["previous_is_active"])
        if not result["allowed"]:
            return result["reason"].upper()
        return (f"TRAFFIC={case['previous']}:100,{case['candidate']}:0 "
                "APP_SCOPE_UNCHANGED")
    if kind == "change_scope":
        impact = classify_changes(case["changes"])
        if "secret" in case["changes"]:
            return (f"NEW_REVISION={'YES' if impact['revision_created'] else 'NO'} "
                    "SECRET_SCOPE=APP RESTART_OR_REDEPLOY_REQUIRED")
        return (f"NEW_REVISION={'YES' if impact['revision_created'] else 'NO'} "
                "APP_IDENTITY_SCOPE=RESOURCE")
    raise ValueError(f"unknown case kind: {kind}")


def main() -> None:
    fixture_path = Path(__file__).with_name("fixtures") / "release-cases.json"
    cases = json.loads(fixture_path.read_text(encoding="utf-8"))
    for name, case in cases.items():
        print(f"{name}: {_run_case(case)}")


if __name__ == "__main__":
    main()