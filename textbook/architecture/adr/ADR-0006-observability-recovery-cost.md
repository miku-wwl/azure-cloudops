# ADR-0006 — Observability, recovery and cost ownership

- Status: Accepted as a reference design; no workspace, backup vault or alert was created.
- Date: 2026-11-27.
- Context: logs, metrics, backups, replication and reserved capacity help operations but incur ongoing or usage-based charges and may contain sensitive data.

## Decision

Assign an owner, scope, retention and access model to each log/metric stream, alert, backup and replicated dataset before enabling it. Route platform and workload evidence to approved destinations, keeping high-cardinality telemetry and verbose diagnostics bounded. Define incident probes and recovery assertions before enabling fault injection. Set RPO/RTO from business needs and test restored data with checksums, dependencies and the same application/business probe.

Keep actual charges, amortized commitment, credits, discounts and forecasts as separate views. Reconcile direct, shared and unallocated cost in integer cents with an explicit deterministic rule. Use budgets and alerts for notification only; they are not a reliable hard cap. Every lab gets an owner, expiry, runtime limit, dependency inventory, teardown and residual audit. Do not delete unrelated resources or assume RG deletion removes detached disks, snapshots, IPs, backups or retained data.

## Consequences

- Richer telemetry and warm/replicated recovery can improve diagnosis and recovery but add storage, ingestion, transfer and compute cost.
- A restore is accepted only after integrity and service behavior are checked; a successful resource create is not recovery evidence.
- Actual cumulative Azure spend remains `NOT_VERIFIED` until delayed billing evidence is reconciled.
- Expensive observability, Backup, Site Recovery, multi-region and security services are design-only for this USD 1.00 project unless a specific experiment clears its own cost and authorization gate.

## Source

- [Azure Monitor pricing](https://azure.microsoft.com/en-us/pricing/details/monitor/) (recheck live rates before use)
- [Azure Backup pricing](https://azure.microsoft.com/en-us/pricing/details/backup/) (recheck service/region and retained-resource costs)
- [Cost Management budgets](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets)
- [Cost allocation and scopes](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/allocate-costs)
- [Azure Policy is not a budget cap](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/cost-mgt-alerts-monitor-usage-spending)
