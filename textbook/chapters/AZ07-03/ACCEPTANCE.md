# AZ07-03 Acceptance — Azure DevOps, Pipelines and Workload Identity Federation

- Status: ACCEPTED for the Stage 1 lecture gate and E5 offline engineering gate.
- Review date: 2026-11-27 (Pacific/Auckland).
- Lecture: 21 / 23; B7 progress is 3/3.

## Publication artifact

- PDF: `textbook/dist/pdf/AZ07-03_azure-devops-pipelines-workload-identity.pdf`
- Pages: 8.
- Size: 1,558,631 bytes.
- SHA-256: `07ed61f35fd4b0d7d74c1ea18f26a4272a7d15db9d0a2f89621b2c0f6789b0a9`
- Publisher QA: 14,067 extracted characters; no placeholder markers or overflow warnings.
- Page fill ratios: cover 21%, pages 2–8: 96%, 91%, 99%, 98%, 98%, 89%, 58%.
- All eight final pages were rendered and visually reviewed at 88 DPI. Pages 6–8 were reviewed at 140 DPI after the final pagination edit; the other pages were unchanged from the prior 140-DPI review. The figures, WIF identity environment variables, version-sensitive issuer warning, plan-contract page, exercises and reference links were checked at readable scale.
- The PDF contains five original editable SVG figures, 17 external source links, three local source-file links and two bookmarks.

## Technical and teaching evidence

- Five figures explain stage/job/step execution and agent workspaces, Azure Repos and resource-owner gates, the WIF trust chain, exact-plan approval, and failure boundaries.
- `labs/azure-pipelines/azure-pipelines.yml` remains an intentionally offline-only pipeline. `enterprise-pipeline.yml` is a separate illustrative pipeline whose `enableCloudDelivery` parameter defaults to `false`; only an explicit compile-time switch includes `templates/enterprise-delivery.yml` with Plan → PlanReview → Apply. Neither pipeline was uploaded, compiled or queued in Azure DevOps.
- The representative enterprise template binds separate Plan/Apply WIF Service Connections, restricted pools, owner-managed Environments, Variable Groups, Secure Files and a current-run plan artifact. It validates the plan before acquiring Apply identity, then calls the E4 controlled apply wrapper. `plan_bundle.py` binds the exact plan bytes to source, target, backend and provider-lock digests and run metadata; its printed summary contains resource addresses/types/actions and output names/actions, never values.
- The custom `cloudops-approval-broker`, production signer/keys, protected trust store, Azure DevOps approval-record verification API, actual WIF connections, protected Environments/checks, required external template, agent pools and persistent/distributed replay lock are external prerequisites, not implementations in this repository. A same-repository include is not a production security boundary; production should enforce a separately protected `extends` template.
- `test_pipeline_yaml.py` checks generic YAML parsing and local structure, not the Azure Pipelines schema compiler. `plan_bundle.py` and `plan_gate.py` used synthetic plan bytes/JSON and temporary fixtures only. The existing plan-gate fixture verifier does not authenticate an approver or authorize Azure access.
- The E5 pipeline suite passed 29 local tests (9 YAML-structure, 8 plan-bundle, 12 plan-gate tests). Full Windows and WSL Python suites each passed 471 tests across 23 lab directories. Windows Terraform 1.15.5 passed recursive fmt, backend-free init/validate in three roots, and 13 plan-only/mock test runs; no remote backend was initialized.
- `textbook/SOURCE_MAP.md` maps Azure DevOps, Microsoft Learn and HashiCorp claims to official documentation and keeps offline evidence separate from server-side behavior.

## Scope and limits

- Azure Repos PR validation, branch policies, WIF federation, Service Connection permissions, Variable Group authorization, Environment checks, agent pool configuration, Pipeline Artifact retention and Azure RBAC were source-analysed only. No Azure DevOps organization or project was accessed, no pipeline was uploaded or queued, and no server-side YAML compile or task execution was claimed.
- The local suite is not an Azure Pipelines schema compiler and does not prove that any service-side resource, approval or WIF trust is configured.
- No Entra token, Azure credential, subscription/ARM query, AzureRM remote provider/backend initialization, cloud plan, resource operation, network request, or billing query was performed. Terraform verification explicitly used `init -backend=false`.
- This chapter's local execution made no Azure or Azure DevOps request and no project Azure resource charge. Actual cumulative Azure spend remains `NOT_VERIFIED`.
- E5's offline engineering gate is complete. Azure DevOps server-side execution, WIF, approval broker, resource-owner checks and live permissions remain `NOT_RUN` and require their own later authorized gate.

## Reproduction

From the repository root:

```powershell
python -m pip install -r textbook/chapters/AZ07-03/labs/azure-pipelines/requirements.txt
python -m unittest discover -s textbook/chapters/AZ07-03/labs/azure-pipelines/tests -p "test_*.py" -v
python textbook/tools/build.py AZ07-03
```
