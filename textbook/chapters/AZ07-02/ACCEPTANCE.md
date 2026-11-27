# AZ07-02 Acceptance — Azure Remote State, Locking and Drift

- Status: ACCEPTED for the offline lecture gate.
- Review date: 2026-11-27 (Pacific/Auckland).
- Lecture: 20 / 23; B7 progress is 2/3.

## Publication artifact

- PDF: `textbook/dist/pdf/AZ07-02_azure-remote-state-locking-drift.pdf`
- Pages: 9 (E4 repagination; the initial Stage 1 artifact had 7 pages).
- Current E4 artifact: 1,670,818 bytes; SHA-256 `6D26AC6269F2BE33097FE20FCBEC007D283D33A8DC6559739186FEB15D027783`.
- Historical Stage 1 artifact: 1,473,825 bytes; SHA-256 `B0F60F1FC0051899726D8BC46B9C7627FAE049B06CC4EF5E1C82A5CCF473440F`.
- Publisher QA: 12,082 extracted characters; no placeholder markers or overflow warnings.
- Page fill ratios: cover 20%; content pages 95%, 95%, 71%, 92%, 77%, 85%, 51%; references 55%.
- All nine final pages were rendered and reviewed at 88 DPI; final experiment pages 7–8 and references page 9 were reviewed at 140 DPI. Six editable figures, including the new controlled-delivery figure, were checked in the rendered PDF.

## Technical and teaching evidence

- Six original editable SVGs explain backend/data-plane boundaries, Blob lease contention, bootstrap and key isolation, normal versus refresh-only drift handling, State recovery, and exact-plan approval.
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
- E4 is complete for the offline gate; E5–E10 and Stage 3 scope/cost/authorization gates remain outstanding for the overall project.

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

## E4 controlled-delivery addendum (2026-11-27)

- Added the controlled-apply chapter section and editable Fig. 20-6. It teaches a signed approval envelope bound to the exact saved plan, commit, environment, subscription/resource group, provider lockfile, operation, approver/time, run/approval IDs and nonce. The chapter distinguishes a local verifier from a real signing service, protected trust root, Azure DevOps server-side Environment checks and distributed replay/lock storage.
- The optional AzureRM backend example retains Entra ID/OIDC settings. It passed only `terraform init -backend=false` and `terraform validate`; remote initialization and Azure Storage access were not run.
- The isolated local lab now verifies built-in `terraform_data` state-only import, zero-diff follow-up plan, `state rm`, configuration rollback, and prior lock/drift/State recovery paths. The import changes Terraform State only; it does not import an external or Azure object.
- Windows and WSL full Python suites each passed 458 tests across 23 directories. The controlled-apply tools suite passed 51 cases with one platform-capability skip. Windows Terraform 1.15.5 passed the repository-wide formatting checks and 13 plan-only test runs across three Terraform roots. WSL has no Terraform CLI.
- No Azure sign-in, subscription/ARM/Storage request, remote State initialization, Azure resource mutation, pricing lookup, network probe or billing query occurred. Actual cumulative Azure spend remains `NOT_VERIFIED`.

## E0 independent-audit addendum (2026-11-27)

- Audit defect: the original automation operated directly in the repository lab root, wrote raw State into ignored `work/` artifacts and had incomplete subprocess timeouts/cleanup when an intermediate command failed. It could overwrite an operator's local Terraform state and evidence.
- Correction: `verify_lab.py` now creates an isolated temporary copy with the locked local provider, enforces per-command and 10-minute total limits, releases or terminates the actual local lock holder on failure, suppresses raw State output, and removes temporary State and files on exit. The separate manual exercise remains explicitly scoped to a disposable local backend and warns operators to inspect existing state first. Existing ignored `work/` evidence was preserved.
- Reverification: the corrected script completed a genuine Windows Terraform v1.15.5/hashicorp-local v2.9.1 lock refusal, content-addressed local-file drift/reconcile and State pull/push recovery. The same plan returned no changes, destroy removed the local marker, and the temporary directory was removed. No Azure provider or endpoint was used. The checkout's existing state/evidence were not modified by this rerun.
- The updated seven-page PDF was rebuilt (8,877 extracted characters; no placeholder markers), rendered as four page-pair sheets, and every page was visually checked. Current artifact: 1,488,101 bytes; SHA-256 `8FC11D572BF1F2B2DC63AF7C407478036781E9FBE68583CA12403A33FFE5BA44`.
- Current full Windows and WSL suites each pass 407 tests across 22 directories. A fresh Windows Terraform pass also confirmed recursive fmt, init/validate for both roots, and all five mock contract tests.
