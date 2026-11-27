# Azure enterprise Terraform reference

This is a source-grounded, opt-in reference root for the AZ07 engineering labs. It contains representative AzureRM modules for networking, a private Linux VM, private AKS and ACR, managed identity and Key Vault RBAC, private Blob storage, Log Analytics, a Recovery Services vault, and one audit-only AzAPI policy assignment. It declares an empty AzureRM remote backend for a later pipeline; the backend target must arrive through an external protected `.tfbackend` file.

## Offline verification

From the repository root:

```powershell
python textbook/tools/verify_terraform.py
```

The runner removes `ARM_*`, `AZURE_*`, and `TF_*` values from its child process, turns off CLI, OIDC, and MSI authentication, uses a temporary empty Terraform CLI config, and executes only format, backend-free init, validate, and Terraform test. The Azure tests declare mock providers and every test run says `command = plan`. The runner never invokes `plan`, `apply`, `destroy`, `az`, or an Azure SDK itself.

Provider installation accesses the Terraform Registry. That is an internet download, not an Azure API call. The version lock file pins the providers and platform checksums.

## Scope and live guards

- All `enable_*` variables default to `false`; target subscription, resource group, region, and name prefix default empty.
- The root consumes an existing resource group and never creates one.
- Enabling any Azure resource requires an exact subscription and resource-group allowlist, an explicit authorization reference and owner-authorization assertion, a reviewed positive gross-cost estimate, a runtime from 1–60 minutes, and a cumulative estimate no higher than USD 0.70 with USD 0.30 reserved under the USD 1.00 project ceiling.
- AKS creates resources in a separate node resource group. Its name must be explicit and separately included in the resource-group allowlist. Live preflight must verify that group does not already exist and that its entire generated resource set is within scope.
- AzureRM provider registration is explicitly `none`; AzAPI registration is skipped. The root contains no provider-registration resource.
- Provider OIDC is an explicit `use_workload_identity` opt-in, default `false`; CLI and MSI fallbacks remain disabled. The remote backend separately requires Entra/OIDC, disables CLI/MSI, and does not discover the Blob endpoint. `init -backend=false` remains the only accepted Stage 2 initialization mode.
- VM administration uses a public SSH key and no public IP. AKS control-plane access is private; node egress uses a Standard Load Balancer. ACR, Key Vault and Blob Storage disable public network access and use private endpoints. Storage disables shared-key and local-user authentication, enables OAuth, TLS 1.2, versioning, and seven-day soft-delete retention.
- Key Vault purge protection is on. A destroy does not erase its soft-deleted retention record immediately; this is a cleanup and residual-resource constraint that must be included in any future live estimate.
- The Recovery Services vault is a vault shell only; no backup policy or protected item is configured. Validate the chosen private network and workload support before enabling it.
- Log Analytics has a 1 GB/day ingestion quota and 30-day retention. Internet ingestion and query remain enabled because this reference does not yet include a Private Link Scope; local authentication is disabled, so Entra authentication is required. Gross ingestion, retention, and other dependent costs still require a current region-specific estimate.
- The local preconditions are accidental-change controls, not a substitute for Azure RBAC, owner authorization, a protected approval system, or independent cost verification. Do not change the guards to make a live deployment fit the USD 1 limit.

The mock provider tests prove Terraform graph and input behavior only. They do not validate Azure API acceptance, regional/SKU availability, DNS resolution, RBAC propagation, or cost. `LIVE_VERIFIED` is not claimed.

## Source references

Versions pinned on 2026-11-27 (Pacific/Auckland): Terraform `>=1.7.0,<2.0.0`, AzureRM `5.15.0`, and AzAPI `2.14.0`. Review the provider changelogs and current service pricing before any future live plan.

- [AzureRM provider, including `resource_provider_registrations = "none"](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [AzureRM provider OIDC guide](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/guides/service_principal_oidc) and [AzureRM backend](https://developer.hashicorp.com/terraform/language/backend/azurerm)
- [AzAPI provider and `skip_provider_registration`](https://registry.terraform.io/providers/Azure/azapi/latest/docs)
- [AzureRM private endpoint](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_endpoint)
- [AzureRM private DNS zone](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_dns_zone)
- [AzureRM Linux virtual machine](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/linux_virtual_machine)
- [AzureRM Kubernetes cluster](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/kubernetes_cluster)
- [AzureRM storage account](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_account)
- [AzureRM Key Vault](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault)
- [AzureRM Container Registry](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/container_registry)
- [AzureRM Log Analytics workspace](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/log_analytics_workspace)
- [AzureRM Recovery Services vault](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/recovery_services_vault)
- [Terraform provider mocks](https://developer.hashicorp.com/terraform/language/tests/mocking)
- [Terraform test command and plan-only runs](https://developer.hashicorp.com/terraform/cli/commands/test)
