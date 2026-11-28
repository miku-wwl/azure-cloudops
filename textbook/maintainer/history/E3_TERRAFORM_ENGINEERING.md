# E3 — Terraform engineering acceptance

**Status:** COMPLETE for Stage 2's offline Terraform engineering gate.
**Date:** 2026-11-27 (Pacific/Auckland).
**Current source:** Windows worktree on `main`; Azure actions are out of scope for E3.

## Delivered configuration

`terraform/azure-enterprise-reference/` is an opt-in reference root using AzureRM `5.15.0` and AzAPI `2.14.0`, with a checked-in `.terraform.lock.hcl`. Reusable modules cover VNet/subnets, private endpoints and DNS, SSH-only Linux VM, private AKS/ACR, user-assigned identity, RBAC-enabled Key Vault, OAuth-only private Blob Storage, Log Analytics, and Recovery Services. The root also contains an AzAPI Resource Manager policy assignment whose effect is explicitly `DoNotEnforce`.

All ten Azure feature flags default to `false`; subscription, existing resource group, region, allowlists, and name prefix default empty. There is no resource-group creation. AzureRM registration is explicitly `none`; AzAPI registration is skipped. Provider CLI and MSI paths are disabled; Provider OIDC is gated by `use_workload_identity`, which defaults to `false`. The private Linux VM has no public IP and accepts an SSH public key only. AKS has a private control plane and must use a separately allowlisted node resource group. Storage, Key Vault, and ACR disable public network access and use private endpoints; Storage disables shared keys. Key Vault enables RBAC and purge protection. State-bearing secrets are not outputs.

**E5 pipeline integration note (2026-11-27):** the Azure reference root now also declares an empty `azurerm` remote backend with Entra/OIDC required and CLI/MSI fallback disabled, so the enterprise pipeline's external protected `.tfbackend` file is accepted by Terraform. The E5 Plan stage's protected tfvars file must set `use_workload_identity = true`; the flag is still false in the root default. Both Windows verification and future local runs must continue to use `terraform init -backend=false`; no remote backend initialization was performed.

`terraform_data.live_scope_guard` checks owner approval assertion/reference, exact subscription and resource-group allowlists, positive verified gross cost estimate, the USD 0.70 planning line plus USD 0.30 contingency inside the USD 1.00 ceiling, a runtime of 1–60 minutes, AKS node resource-group scope, and service-specific required inputs. These local preconditions reduce accidental plans; they do not prove approval or replace Azure RBAC and protected change controls.

## Verification

- Terraform `1.15.5`, Windows: recursive format checks passed for `chapters` and `terraform`; backend-free `init`, `validate`, and `test` passed in all three Terraform roots.
- The Azure reference root passed eight Terraform test runs. Every test uses `mock_provider` and `command = plan`; coverage includes the default-disabled plan, network, private Storage, audit-only AzAPI policy, all ten feature categories together, and rejected approval/scope/budget cases.
- The other roots passed their three and two existing plan-only runs. Total Terraform tests: 13 runs across 3 roots.
- The `verify_terraform.py` child process removes `ARM_*`, `AZURE_*` and `TF_*` variables, disables CLI/OIDC/MSI environment auth, uses an empty temporary Terraform CLI config, and runs no `az`, apply or destroy command.
- Windows and WSL `devops-lab` Python suites each passed **429 tests across 23 directories**. Static contract tests check every repository Terraform test run is `plan`-only and directly exercise the runner's environment-scrubbing function. WSL has no Terraform CLI, so Terraform CLI/provider-schema verification ran on Windows only.
- The AZ07-01 chapter now describes the E3 reference root. Its rebuilt PDF has 9 pages, 11,981 extracted characters, no placeholder or overflow markers, and SHA-256 `19C9C7A4BB23FF258214EC2954A016271C043B0D2B9236C1EE7931831C4674A5`. All nine pages were rendered and visually reviewed at 88 and 140 DPI; the exercise heading/content page split was corrected.

Provider packages were downloaded from Terraform Registry. That is internet access, not an Azure API request. Tests use mock providers, no Azure credentials, and synthetic identifiers; no Azure sign-in, subscription/billing/resource query, resource-provider registration, live plan, apply, destroy, DNS probe, or billing call was made. Actual project Azure spend remains `NOT_VERIFIED`.

## Operational limits before any future live use

- Log Analytics Internet ingestion/query are `Enabled` with local authentication disabled. This means Entra authorization is required, but the module does not yet provide an Azure Monitor Private Link Scope.
- The Recovery Services vault has no backup policy, protected item or demonstrated private connectivity. It is not evidence of a usable backup/restore path.
- Key Vault purge protection and soft-delete retention mean `destroy` does not immediately remove its soft-deleted record. Include that retention and any other residue in cleanup and cost estimates.
- Azure API acceptance, region/SKU availability, provider registration status, DNS, identity/role propagation, external approval enforcement, cost, and actual billing are unverified. Recheck exact live scope and current pricing before a separately authorized batch. Do not treat the mock fixtures' USD 0.10 sample as a price estimate.
- The final Stage 2 publication ZIPs need regeneration and byte verification after all remaining E4–E10 changes.

## Primary references reviewed

- [AzureRM 5.15.0 provider documentation](https://registry.terraform.io/providers/hashicorp/azurerm/5.15.0/docs) — provider auth and resource-provider registration; its `none` setting prevents automatic registration.
- [AzAPI 2.14.0 provider documentation](https://registry.terraform.io/providers/Azure/azapi/2.14.0/docs) — ARM resources and registration opt-out.
- [Terraform provider mocking](https://developer.hashicorp.com/terraform/language/tests/mocking) — mocked provider values for plan tests.
- [Terraform tests](https://developer.hashicorp.com/terraform/language/tests) — plan-only commands and expected failures.
- Resource documentation for [Kubernetes cluster](https://registry.terraform.io/providers/hashicorp/azurerm/5.15.0/docs/resources/kubernetes_cluster), [Storage account](https://registry.terraform.io/providers/hashicorp/azurerm/5.15.0/docs/resources/storage_account), [Key Vault](https://registry.terraform.io/providers/hashicorp/azurerm/5.15.0/docs/resources/key_vault), [Container Registry](https://registry.terraform.io/providers/hashicorp/azurerm/5.15.0/docs/resources/container_registry), [Log Analytics workspace](https://registry.terraform.io/providers/hashicorp/azurerm/5.15.0/docs/resources/log_analytics_workspace), [Private Endpoint](https://registry.terraform.io/providers/hashicorp/azurerm/5.15.0/docs/resources/private_endpoint), and [Recovery Services vault](https://registry.terraform.io/providers/hashicorp/azurerm/5.15.0/docs/resources/recovery_services_vault).
