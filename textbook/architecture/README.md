# Azure CloudOps architecture set

**Status:** E1 design baseline, 2026-11-27. These are three separate architecture views with different purposes. They do not describe a deployed customer environment or authorize Azure changes.

| View | Purpose | Evidence state |
|---|---|---|
| [Enterprise reference architecture](enterprise-reference.md) | Target design for a governed multi-subscription enterprise | DESIGNED; no tenant deployment |
| [Local learning architecture](local-learning.md) | Executable workstation/WSL lab boundary and local verification path | LOCAL_VERIFIED for listed checks; Kubernetes engine unavailable at last check |
| [Conditional live lab](conditional-live-lab.md) | Small, temporary Azure scope to consider after Stage 3 gates | DESIGNED; NOT_RUN |

## Architecture decisions

1. [ADR-0001 — Governance and subscription boundaries](adr/ADR-0001-governance-subscription-boundaries.md)
2. [ADR-0002 — Hub-spoke and Virtual WAN](adr/ADR-0002-hub-spoke-vwan.md)
3. [ADR-0003 — Private connectivity and DNS](adr/ADR-0003-private-connectivity-dns.md)
4. [ADR-0004 — Identity, RBAC and Policy](adr/ADR-0004-identity-rbac-policy.md)
5. [ADR-0005 — Terraform state and controlled delivery](adr/ADR-0005-terraform-state-delivery.md)
6. [ADR-0006 — Observability, recovery and cost ownership](adr/ADR-0006-observability-recovery-cost.md)

The enterprise view is intentionally richer than the local and conditional-live views. Components such as Azure Firewall, ExpressRoute, Virtual WAN, Bastion, Private Resolver, Sentinel, AKS and multi-region recovery are design options; they are not deployed and must not be inferred from a local simulation.
