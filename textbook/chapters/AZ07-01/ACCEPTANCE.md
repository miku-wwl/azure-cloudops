# AZ07-01 Acceptance — Terraform Core, Provider, Graph, State, Plan and Import

- Status: ACCEPTED for the offline lecture gate.
- Review date: 2026-11-27 (Pacific/Auckland).
- Lecture: 19 / 23; B7 progress is 1/3.

## Publication artifact

- PDF: textbook/dist/pdf/AZ07-01_terraform-core-provider-graph-state-plan-import.pdf
- Pages: 9.
- Size: 1,634,307 bytes.
- SHA-256: 19C9C7A4BB23FF258214EC2954A016271C043B0D2B9236C1EE7931831C4674A5
- Publisher QA: 11,981 extracted characters; no placeholder markers or overflow warnings.
- Page fill ratios: 25%, 96%, 99%, 75%, 65%, 91%, 96%, 31%, 69%.
- All nine pages were rendered and visually reviewed at 88 and 140 DPI. Pages 7–9 were rechecked after the E3 extension and exercise reflow.

## Technical and teaching evidence

- Five original editable SVG figures cover Core / Provider / ARM boundaries, dependency ordering, State bindings and drift, Plan review, and import lifecycle.
- The Terraform CLI lab uses only Terraform's built-in terraform_data resource and a local child module. It has no AzureRM/AzAPI provider, credential, remote backend, Azure resource ID or ARM endpoint.
- On Windows, Terraform v1.15.5: init with backend=false passed; validate passed; all three plan-only terraform test runs passed, including expected variable-validation failures. No apply or destroy was run.
- terraform fmt -check -recursive -diff textbook/chapters passed.
- The standard-library core-model lab passed 26 local tests.
- Full Python suites passed on Windows and in WSL: 336 tests across 19 lab directories in each environment.
- textbook/SOURCE_MAP.md maps claims to primary HashiCorp, AzureRM/AzAPI Registry and Microsoft Learn sources, and separates documented behavior from local results.

## Scope and limits

- The Python lab is a small deterministic teaching model. It is not Terraform Core, AzureRM/AzAPI, Azure API, real State, or a live Plan emulator.
- WSL did not have the Terraform CLI installed. Terraform CLI formatting, initialization, validation and tests therefore ran on Windows only; WSL ran the full Python suite.
- Microsoft Learn's AzureRM/AzAPI choice and migration pages identify AI-generated content; the chapter records that caveat and cross-checks the claims against official HashiCorp and Registry documentation.
- No Azure sign-in, Azure/ARM/Entra query, Azure provider initialization or registration, resource mutation, live plan/import, network probe, or billing query was performed.
- This chapter's local execution made no Azure request or project Azure resource charge. Actual cumulative Azure spend remains NOT_VERIFIED.
- Stage 2 E3 Terraform engineering and Stage 3 authorization/cost gates remain outstanding for the overall project.

## E3 engineering addendum (2026-11-27)

- Added a separate AzureRM/AzAPI reference root plus reusable modules for networking, private endpoints, Linux VM, AKS, ACR, managed identity, Key Vault, private Storage, Log Analytics, and supporting services. The root uses an existing resource group and enables no Azure resources by default.
- Locked `hashicorp/azurerm` 5.15.0 and `Azure/azapi` 2.14.0 after current-version verification and successful Windows provider installation. `terraform validate` checked all module resource schemas. AzureRM resource-provider registration is `none`; AzAPI registration is skipped; provider CLI/MSI/OIDC login is disabled for this root.
- Windows Terraform 1.15.5: repository-wide chapter/terraform recursive fmt check passed; backend-free init, validate, and Terraform tests passed in all three Terraform roots. AZ07 E3 mock suite passed 8/8; all eight runs specify `command = plan`. Full Windows Python suite passed 428 tests across 23 directories.
- Test runner removes Azure credential and `TF_*` override environment variables. It makes no Azure API call and invokes no Azure apply/destroy. Provider packages were downloaded from Terraform Registry. Provider schema validation and mocked plans are local evidence only.
- Actual Azure authorization, regional support, private DNS, RBAC propagation, service functionality, live pricing and actual billing remain unverified. The guard defaults remain closed; no Azure resource, billing or subscription request was made.

## Reproduction

From the repository root:

```powershell
python -m unittest discover -s textbook/chapters/AZ07-01/labs/core-model -p "test_*.py" -v
terraform -chdir=textbook/chapters/AZ07-01/labs/terraform-core init -backend=false -input=false
terraform -chdir=textbook/chapters/AZ07-01/labs/terraform-core validate -no-color
terraform -chdir=textbook/chapters/AZ07-01/labs/terraform-core test -no-color
python textbook/tools/build.py AZ07-01
```

The full Windows and WSL suite results are summarized in textbook/PROGRESS.md and textbook/VERIFICATION_MATRIX.md.
