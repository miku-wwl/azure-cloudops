# ADR-0005 — Terraform state and controlled delivery

- Status: Accepted as the target engineering contract; Azure backend and pipeline are not deployed.
- Date: 2026-11-27.
- Context: state contains resource identifiers and configuration data; locking must coordinate writers; a reviewed plan must be bound to the identity, environment and scope that will apply it.

## Decision

Use separate state boundaries for workload/environment with stable keys and a restricted backend Storage container. Bootstrap backend storage with a separately reviewed process. Prefer Microsoft Entra data-plane authentication for the `azurerm` backend. Grant state read/write only to the infrastructure identity at the state container scope; do not infer state access from ARM Contributor. Never commit raw state, plan files, backend credentials or provider caches.

Use an offline pipeline/test contract first. For a future controlled Azure delivery pipeline, require: protected source revision; pinned tool/provider versions; format/validate/test; plan generated for a single environment/subscription/resource-group contract; immutable plan artifact plus digest; approval bound to that digest; short validity; same identity/scope for plan/apply as appropriate; replay protection; post-apply verification; and cleanup/incident route. Any changed source, plan bytes, scope, identity, expiry or approval must fail closed. The plan contract must be checked at the trusted apply boundary, not only by a caller-supplied JSON file.

## Consequences

- Remote State enables collaboration and locking but creates a sensitive storage dependency and a separate data-plane permission path.
- Separate keys reduce cross-environment risk but require explicit backup, lineage and recovery procedures.
- Offline YAML parsing and synthetic plan tests do not establish Azure DevOps server behavior, WIF, service-connection scope or AzureRM provider behavior.
- No Azure backend, Service Connection, federation credential or apply action may be introduced during Stage 2.

## Source

- [Terraform azurerm backend](https://developer.hashicorp.com/terraform/language/backend/azurerm)
- [Terraform state locking](https://developer.hashicorp.com/terraform/language/state/locking)
- [Azure Pipelines WIF service connection](https://learn.microsoft.com/en-us/azure/devops/pipelines/release/configure-workload-identity?view=azure-devops)
- [Azure Pipelines approvals and checks](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops)
