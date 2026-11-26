# AZ07-03 Acceptance — Azure DevOps, Pipelines and Workload Identity Federation

- Status: ACCEPTED for the offline lecture gate.
- Review date: 2026-11-27 (Pacific/Auckland).
- Lecture: 21 / 23; B7 progress is 3/3.

## Publication artifact

- PDF: `textbook/dist/pdf/AZ07-03_azure-devops-pipelines-workload-identity.pdf`
- Pages: 7.
- Size: 1,480,789 bytes.
- SHA-256: `ab0c23fa3f97beceb75a71d11df2087389e9856efa612e463feca2da4c820d65`
- Publisher QA: 11,548 extracted characters; no placeholder markers or overflow warnings.
- Page fill ratios: cover 21%, body pages 96%, 91%, 99%, 99%, 85%, references 76%.
- All seven pages were rendered and visually reviewed at 88 and 140 DPI. The figures, WIF identity environment variables, version-sensitive issuer warning, plan-contract page, exercises and reference links were checked at readable scale.
- The PDF contains five original editable SVG figures, 17 external source links, three local source-file links and two bookmarks.

## Technical and teaching evidence

- Five figures explain stage/job/step execution and agent workspaces, Azure Repos and resource-owner gates, the WIF trust chain, exact-plan approval, and failure boundaries.
- `labs/azure-pipelines/azure-pipelines.yml` is an intentionally offline-only pipeline with `trigger: none`, a single self checkout with `persistCredentials: false`, and a reusable steps template. It contains no Azure task, service connection, cloud login, Terraform Apply, or destroy.
- `test_pipeline_yaml.py` parses the pipeline and template as generic YAML and checks the local structure. The pool name `CloudOps-Offline` is an illustrative organization-side prerequisite; this repository did not create or configure an Azure DevOps pool.
- `scripts/plan_gate.py` was executed against temporary synthetic plan bytes and approval fixtures: one valid contract passed; 11 negative cases rejected plan tampering, wrong commit/target/provider lock/run, expired or overlong validity, future approval, self-approval and missing timezone.
- The plan verifier checks hashes and metadata consistency only. It does not parse a Terraform plan, authenticate an approver, call Azure DevOps, or authorize Azure access. Synthetic fixtures were deleted with their temporary directory.
- Full Windows and WSL Python suites each passed 353 tests across 20 lab directories after this lecture was added.
- `textbook/SOURCE_MAP.md` maps Azure DevOps, Microsoft Learn and HashiCorp claims to official documentation and keeps offline evidence separate from server-side behavior.

## Scope and limits

- Azure Repos PR validation, branch policies, WIF federation, Service Connection permissions, Variable Group authorization, Environment checks, agent pool configuration, Pipeline Artifact retention and Azure RBAC were source-analysed only. No Azure DevOps organization or project was accessed, no pipeline was uploaded or queued, and no server-side YAML compile or task execution was claimed.
- The local suite is not an Azure Pipelines schema compiler and does not prove that any service-side resource, approval or WIF trust is configured.
- No Entra token, Azure credential, subscription/ARM query, AzureRM provider/backend initialization, cloud plan, resource operation, network request, or billing query was performed.
- This chapter's local execution made no Azure request or project Azure resource charge. Actual cumulative Azure spend remains `NOT_VERIFIED`.
- Stage 2 E5 still must integrate the plan contract into enterprise Azure Pipelines, add complete plan/apply controls and concurrency/negative tests, and validate offline scripts. Azure DevOps server-side execution and WIF remain `NOT_RUN` until an authorized later gate.

## Reproduction

From the repository root:

```powershell
python -m pip install -r textbook/chapters/AZ07-03/labs/azure-pipelines/requirements.txt
python -m unittest discover -s textbook/chapters/AZ07-03/labs/azure-pipelines/tests -p "test_*.py" -v
python textbook/tools/build.py AZ07-03
```
