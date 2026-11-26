# AZ07-02 Acceptance — Azure Remote State, Locking and Drift

- Status: ACCEPTED for the offline lecture gate.
- Review date: 2026-11-27 (Pacific/Auckland).
- Lecture: 20 / 23; B7 progress is 2/3.

## Publication artifact

- PDF: `textbook/dist/pdf/AZ07-02_azure-remote-state-locking-drift.pdf`
- Pages: 7.
- Size: 1,473,825 bytes.
- SHA-256: `B0F60F1FC0051899726D8BC46B9C7627FAE049B06CC4EF5E1C82A5CCF473440F`
- Publisher QA: 8,770 extracted characters; no placeholder markers or overflow warnings.
- Page fill ratios: cover 20%, then 95%, 95%, 71%, 92%, 87%, references 37%.
- All seven pages were rendered and reviewed at 88 and 140 DPI; pages 2–6 were also inspected at full 140 DPI. All five mechanism figures were checked in the rendered PDF.

## Technical and teaching evidence

- Five original editable SVGs explain backend/data-plane boundaries, Blob lease contention, bootstrap and key isolation, normal versus refresh-only drift handling, and State recovery.
- The local lab uses the local backend plus `hashicorp/local` v2.9.1, pinned in `.terraform.lock.hcl`. It has no AzureRM/AzAPI provider, Azure credentials, remote backend, Azure resource ID, or ARM endpoint.
- Windows Terraform v1.15.5: init downloaded the signed provider; validate passed; both Terraform test plan contracts passed; repository-wide `terraform fmt -check -recursive -diff textbook/chapters` passed.
- The real local lock run held one Terraform apply behind a local named-pipe gate, then ran a second Terraform plan against the same State. Terraform returned `Error acquiring the state lock`; the Windows local backend diagnostic reported that another process had locked a portion of `terraform.tfstate`. No sleep or fabricated lock output was used.
- A manual file edit produced `terraform plan -detailed-exitcode` exit code 2 and a `+ create` plan. With local provider v2.9.1, `local_file` treats the edited content as the original resource disappearing; refresh-only removed the State binding without changing the file; normal apply then restored the declared content. This is provider-specific local evidence, not a universal drift mapping.
- `terraform state pull` captured a backup with lineage and serial. After moving the local State file aside, `terraform state list` reported no State; `terraform state push` restored `local_file.marker`; the next plan had exit code 0 and no diff. `terraform destroy` then removed the local file resource. Actual outputs are in ignored `textbook/chapters/AZ07-02/labs/terraform-state/work/verification.log`.
- Full Windows and WSL Python suites each passed 336 tests across 19 lab directories. Windows Terraform checks validated three `main.tf` directories (including the AZ07-01 child module) and passed five plan tests across the two lecture roots. WSL does not have Terraform CLI installed.
- `textbook/SOURCE_MAP.md` classifies each Azure claim as source-analysed, each local observation as locally verified, and Azure backend execution as not run.

## Scope and limits

- The AzureRM backend, Blob lease protocol, data-plane roles, versioning and soft-delete behavior are source-analysed from official HashiCorp and Microsoft documentation; none was configured or queried against Azure.
- The local backend test uses Windows file locking, not Azure Blob lease semantics. The local provider drift path is deliberately documented as specific to v2.9.1 and `local_file`.
- No Azure sign-in, subscription/ARM/Entra query, Azure provider initialization or registration, Azure Storage request, Azure resource mutation, network probe, live plan/import, or billing query was performed.
- This chapter made no Azure request or project Azure resource charge. Actual cumulative Azure spend remains `NOT_VERIFIED`.
- Stage 2 E3/E4 engineering and Stage 3 scope/cost/authorization gates remain outstanding for the overall project.

## Reproduction

From the repository root:

```powershell
python textbook/tools/build.py AZ07-02
terraform -chdir=textbook/chapters/AZ07-02/labs/terraform-state init -input=false
terraform -chdir=textbook/chapters/AZ07-02/labs/terraform-state validate -no-color
terraform -chdir=textbook/chapters/AZ07-02/labs/terraform-state test -no-color
python textbook/chapters/AZ07-02/labs/terraform-state/scripts/verify_lab.py
terraform fmt -check -recursive -diff textbook/chapters
```

The verification script exercises actual local Terraform locking, provider-specific file drift, backup and State restoration, then destroys the local managed file. The Windows and WSL full Python suite results are recorded in `textbook/PROGRESS.md`.