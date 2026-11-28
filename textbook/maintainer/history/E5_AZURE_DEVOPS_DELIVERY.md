# E5 — Azure Pipelines Delivery Engineering

- Status: E5 offline engineering gate complete.
- Date: 2026-11-27 (Pacific/Auckland).
- Scope: representative Azure DevOps Plan → PlanReview → Apply controls, local validation, and accurate publication of limits. Stage 2 remains offline and does not create or modify Azure resources.

## Delivered

- `chapters/AZ07-03/labs/azure-pipelines/enterprise-pipeline.yml` is a manually invoked representative pipeline. `enableCloudDelivery` defaults to `false`; the enterprise delivery stages are included only through an explicit compile-time parameter. The existing `azure-pipelines.yml` remains the offline-only teaching pipeline.
- `templates/enterprise-delivery.yml` describes three stages. Plan uses a scoped WIF Service Connection and owner-provided secure backend/variable files, then emits a saved plan and a redacted summary artifact. PlanReview binds an owner-managed Environment, downloads only the current run's artifact, and verifies the plan contract without Azure identity. Apply binds a separate Environment and WIF identity, checks the artifact/backend/lock/source/scope before identity acquisition, then invokes E4's controlled apply wrapper.
- `scripts/plan_bundle.py` creates and verifies a manifest bound to Git SHA, run ID, environment and target, backend configuration digest, provider lock digest, exact saved-plan bytes, and redacted action summary. It checks subscription and resource-group values from Terraform plan variables, rejects unsupported action/JSON forms and duplicate properties, and prints no resource/output values. Bundles and backend inputs must stay outside the repository.
- `azure-enterprise-reference` now declares an AzureRM OIDC/Entra-auth backend while keeping AzureRM and AzAPI provider WIF opt-in (`use_workload_identity = false` by default). Stage 2 Terraform checks explicitly use `init -backend=false`; remote state and cloud identity were not accessed.
- AZ07-03 was expanded with the execution boundary, ownership model, exact artifact checks, pre-identity Apply verification, external prerequisites and exercises. Its final PDF has eight pages and five editable SVG figures.

## Verification evidence

- E5 suite: 29 tests passed — 9 YAML structure tests, 8 plan-bundle tests and 12 existing plan-gate tests.
- Full offline Python suite: Windows Python 3.13.9 and WSL Python 3.12.3 each passed 471 tests across 23 directories.
- Terraform: version 1.15.5 passed recursive format checks, backend-free init/validate for three roots, and 13 plan-only/mock runs. The Azure root's eight mock scenarios passed. No Azure backend was initialized.
- PDF: publisher report shows 8 pages, 14,067 extracted characters, no placeholder markers and no overflow warnings. Fill ratios are 21% on the cover and 96%, 91%, 99%, 98%, 98%, 89% and 58% on pages 2–8. All pages were rendered and visually inspected at 88 DPI; pages 6–8 were also reviewed at 140 DPI after the final pagination edit.
- Artifact: `dist/pdf/AZ07-03_azure-devops-pipelines-workload-identity.pdf`, 1,558,631 bytes, SHA-256 `07ed61f35fd4b0d7d74c1ea18f26a4272a7d15db9d0a2f89621b2c0f6789b0a9`.
- `git diff --check` and the final E5 and Terraform checks are part of the checkpoint verification.

## External prerequisites and limits

The YAML is an illustrative template, not a server-tested pipeline. Generic PyYAML parsing does not compile Azure Pipelines YAML. No Azure DevOps organization was accessed and no pipeline was uploaded, queued or run. The following production-side controls are not configured or implemented here:

- Azure DevOps WIF Service Connections, Entra federated credentials and minimum Azure/Storage roles.
- Owner-managed PlanReview/Apply Environments and checks; variable-group and Secure File authorization; protected agent pools.
- Azure Repos target-branch Build Validation policy and required template policy. A same-repository `include` is not a production trust boundary; production should enforce a separately protected external `extends` template.
- `cloudops-approval-broker`, signer/key management, protected trust store, verification of real Azure DevOps run/check/approver records, and replay protection shared across every Apply agent. The broker call is an integration boundary, not a delivered implementation.
- Persistent Terraform control state and a distributed lock if more than one Apply agent or external writer can operate on the target.

The plan verifier authenticates no person and grants no Azure access. Synthetic plan bytes and JSON fixtures establish local parser and binding behavior only. Azure authentication, remote backend initialization, cloud planning, resource operations, network requests, Azure DevOps requests and billing queries were not performed. Actual cumulative Azure spend remains `NOT_VERIFIED`; do not report USD 0.00.

## Primary source references

- [Azure Pipelines approvals and checks](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops)
- [Azure Pipelines environments](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/environments?view=azure-devops)
- [Azure Pipelines workload identity federation](https://learn.microsoft.com/en-us/azure/devops/pipelines/release/configure-workload-identity?view=azure-devops)
- [AzureCLI@2 task reference](https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/azure-cli-v2?view=azure-pipelines)
- [Azure Pipelines templates](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/templates?view=azure-devops)
- [Azure Pipeline artifacts](https://learn.microsoft.com/en-us/azure/devops/pipelines/artifacts/pipeline-artifacts?view=azure-devops)
- [Terraform AzureRM backend](https://developer.hashicorp.com/terraform/language/backend/azurerm)
- [AzureRM provider OIDC guide](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/guides/service_principal_oidc)

## Reproduction

From the repository root:

```powershell
python -m unittest discover -s textbook/chapters/AZ07-03/labs/azure-pipelines/tests -p "test_*.py" -v
python textbook/tools/verify_terraform.py
python textbook/tools/build.py AZ07-03
```
