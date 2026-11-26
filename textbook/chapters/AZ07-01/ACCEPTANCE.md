# AZ07-01 Acceptance — Terraform Core, Provider, Graph, State, Plan and Import

- Status: ACCEPTED for the offline lecture gate.
- Review date: 2026-11-27 (Pacific/Auckland).
- Lecture: 19 / 23; B7 progress is 1/3.

## Publication artifact

- PDF: textbook/dist/pdf/AZ07-01_terraform-core-provider-graph-state-plan-import.pdf
- Pages: 8.
- Size: 1,556,167 bytes.
- SHA-256: f97417d58cba31e0298f24aafc7ed67e5c3bd442d6fb379594967c2fbca629d
- Publisher QA: 9,890 extracted characters; no placeholder markers or overflow warnings.
- Page fill ratios: 25%, 96%, 99%, 75%, 65%, 91%, 62%, 59%.
- All eight pages were rendered and visually reviewed at 88 and 140 DPI. Pages 7–8 were rechecked after the last reference update.

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
