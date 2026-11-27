#!/usr/bin/env python
"""Small, offline FinOps ledger contract over a synthetic JSON fixture.

This is a teaching model, not an Azure bill parser, pricing engine, RBAC check,
cost allocation service, reservation matcher, or deletion tool.
"""

import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).parent
FIXTURE = ROOT / "synthetic-ledger.json"
CENT = Decimal("0.01")


class ContractError(ValueError):
    pass


def money(value):
    try:
        result = Decimal(str(value)).quantize(CENT)
    except (InvalidOperation, ValueError) as exc:
        raise ContractError(f"invalid money value: {value!r}") from exc
    if not result.is_finite():
        raise ContractError(f"non-finite money value: {value!r}")
    return result


def validate(data):
    selected_view = data.get("selected_view")
    if selected_view not in {"actual", "amortized"}:
        raise ContractError("selected_view must be actual or amortized")

    currencies = set()
    seen = set()
    for row in data.get("cost_records", []):
        record_id = row.get("id")
        view = row.get("view")
        if not record_id or view not in {"actual", "amortized"}:
            raise ContractError("every cost record needs an id and a valid view")
        if (record_id, view) in seen:
            raise ContractError(f"duplicate record id within view: {record_id}")
        seen.add((record_id, view))
        currencies.add(row.get("currency"))
        money(row.get("amount"))
    if len(currencies) != 1 or None in currencies:
        raise ContractError("one explicit currency is required for the selected fixture")
    return selected_view


def effective_cost_center(row):
    direct = row.get("tags", {}).get("costCenter")
    if direct:
        return direct
    inherited = row.get("group_tags", {}).get("costCenter")
    if row.get("tag_inheritance_enabled") and inherited:
        return inherited
    return None


def summarize(data, view=None):
    selected = view or validate(data)
    if selected not in {"actual", "amortized"}:
        raise ContractError("view must be actual or amortized")
    rows = [row for row in data["cost_records"] if row["view"] == selected]
    if not rows:
        raise ContractError(f"fixture contains no {selected} records")

    gross = Decimal("0.00")
    credits = Decimal("0.00")
    allocations = {}
    shared_allocations = {}
    unallocated = Decimal("0.00")

    for row in rows:
        amount = money(row["amount"])
        if amount < 0:
            if row.get("kind") in {"credit", "refund"}:
                credits += -amount
            else:
                raise ContractError(f"negative charge must be a credit/refund: {row['id']}")
            continue
        gross += amount
        if amount == 0 or row.get("allocatable") is False:
            if row.get("allocatable") is False:
                unallocated += amount
            continue

        weights = row.get("shared_weights")
        if weights is not None:
            if not weights or any(money(weight) < 0 for weight in weights.values()):
                raise ContractError(f"shared weights must be nonnegative: {row['id']}")
            weight_total = sum((money(weight) for weight in weights.values()), Decimal("0.00"))
            if weight_total != Decimal("100.00"):
                raise ContractError(f"shared weights must total 100: {row['id']}")
            for cost_center, weight in weights.items():
                share = (amount * money(weight) / Decimal("100")).quantize(CENT)
                allocations[cost_center] = allocations.get(cost_center, Decimal("0.00")) + share
                shared_allocations[cost_center] = shared_allocations.get(cost_center, Decimal("0.00")) + share
            continue

        cost_center = effective_cost_center(row)
        if cost_center:
            allocations[cost_center] = allocations.get(cost_center, Decimal("0.00")) + amount
        else:
            unallocated += amount

    allocated = sum(allocations.values(), Decimal("0.00"))
    if allocated + unallocated != gross:
        raise ContractError("allocation does not reconcile to gross charges")

    return {
        "view": selected,
        "currency": next(iter({row["currency"] for row in rows})),
        "gross_charges": gross.quantize(CENT),
        "credits": credits.quantize(CENT),
        "net_cost": (gross - credits).quantize(CENT),
        "allocated_gross": allocated.quantize(CENT),
        "unallocated_gross": unallocated.quantize(CENT),
        "by_cost_center": {key: value.quantize(CENT) for key, value in sorted(allocations.items())},
        "shared_by_cost_center": {key: value.quantize(CENT) for key, value in sorted(shared_allocations.items())},
    }


def budget_status(data):
    budget = data["budget"]
    limit = money(budget["amount"])
    actual = money(budget["actual_cost"])
    forecast = money(budget["forecast_cost"])
    return {
        "threshold_crossed_by_actual": actual >= limit,
        "threshold_crossed_by_forecast": forecast >= limit,
        "control": "alert_only",
        "consumption_stopped": False,
    }


def commitment_utilization(data):
    results = []
    for item in data["commitments"]:
        hourly = money(item["hourly_commitment"])
        if hourly <= 0 or not item["eligible_use_by_hour"]:
            raise ContractError(f"commitment needs a positive hourly amount and hourly samples: {item['id']}")
        committed = Decimal("0.00")
        covered = Decimal("0.00")
        unused = Decimal("0.00")
        for eligible_use in item["eligible_use_by_hour"]:
            use = money(eligible_use)
            if use < 0:
                raise ContractError(f"eligible use cannot be negative: {item['id']}")
            committed += hourly
            covered += min(hourly, use)
            unused += max(Decimal("0.00"), hourly - use)
        percent = (covered / committed * Decimal("100")).quantize(CENT)
        results.append({
            "id": item["id"],
            "committed": committed.quantize(CENT),
            "covered": covered.quantize(CENT),
            "unused_expired": unused.quantize(CENT),
            "utilization_percent": percent,
            "unused_rolls_over": False,
        })
    return results


def recovery_decisions(data):
    decisions = []
    for item in data["resource_candidates"]:
        state = item["power_state"]
        residuals = item.get("residual_resources", [])
        retention = item.get("retention_required", [])
        approved = item.get("owner_approved", False)
        if state == "Stopped":
            decision = "review_owner_before_deallocate"
            compute_billed = True
        elif state == "Deallocated":
            decision = "inspect_persistent_resources" if residuals else "verify_related_meters"
            compute_billed = False
        elif state == "Deleted" and retention:
            decision = "retain_required_resources"
            compute_billed = False
        elif state == "Deleted" and residuals and not approved:
            decision = "owner_review_required"
            compute_billed = False
        elif state == "Deleted" and residuals and approved:
            decision = "eligible_for_approved_cleanup"
            compute_billed = False
        elif state == "Deleted":
            decision = "inspect_cost_refresh"
            compute_billed = False
        else:
            decision = "investigate_unknown_state"
            compute_billed = None
        decisions.append({
            "id": item["id"],
            "decision": decision,
            "compute_billed": compute_billed,
            "residual_resources": residuals,
            "execution_performed": False,
        })
    return decisions


def analyze(data):
    validate(data)
    return {
        "fixture": "synthetic-only",
        "ledger": summarize(data),
        "budget": budget_status(data),
        "commitments": commitment_utilization(data),
        "recovery_decisions": recovery_decisions(data),
        "azure_requests": 0,
        "resource_changes": 0,
    }


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else FIXTURE
    try:
        result = analyze(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, KeyError, ContractError) as exc:
        print(f"FIN-01 contract error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
