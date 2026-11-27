# ADR-0001 — Governance and subscription boundaries

- Status: Accepted as the project reference design; no Azure change authorized.
- Date: 2026-11-27.
- Context: a bank-like workload needs ownership, policy inheritance, environment isolation, quota/billing visibility and controlled platform/workload responsibilities.

## Decision

Use one Entra tenant for the reference estate unless a documented sovereignty, identity or organizational requirement establishes a separate tenant. Organize subscriptions under a small management-group hierarchy: platform, workload landing zones, sandbox and decommissioned. Create dedicated connectivity, management and identity subscriptions only where their capabilities and owners exist. Separate production from development/test when ownership, security, quota or change controls require independent boundaries; do not force a one-subscription-per-environment rule where it adds no useful isolation.

Treat management groups as governance inheritance, subscriptions as billing/quota/ownership and security boundaries, and resource groups as resource lifecycle boundaries. Put workload role assignments below the Policy scope so workload teams cannot alter the guardrails that govern them. Use a subscription-vending contract to record owner, region, allowed resource types, network integration, identity groups, cost center, logs and expiry.

## Consequences

- Platform policy and connectivity have explicit owners; workload teams retain autonomy inside scoped guardrails.
- More subscriptions improve separation but add quota, access, policy, inventory and operational work.
- Management-group changes can affect many subscriptions, so policy assignments require staged audit and a separately approved rollout.
- This design is not a claim that the user's real tenant has this hierarchy.

## Source

- [Azure landing-zone overview](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/)
- [Manage application development environments](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/design-area/management-application-environments)
- [Landing-zone identity and access management](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/design-area/identity-access-landing-zones)
