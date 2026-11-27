# AZ07-02 local Terraform state lab

This lab verifies Terraform CLI behavior against a disposable file and local state. It has no `azurerm` or `azapi` provider, Azure credentials, remote backend, Azure resource ID, or ARM endpoint. The `local_file.marker` resource writes only `work/managed-marker.txt` under this lab directory. Terraform state and the provider lock file remain local.

## Requirements

- Terraform CLI 1.10 or later (recorded run: Windows Terraform 1.15.5)
- Python 3.10 or later, for the lock holder and verification script
- Network access only for the first `terraform init` to download the pinned `hashicorp/local` provider. This is a Terraform Registry package fetch, not an Azure request.

Run all commands from this directory. The root `.gitignore` excludes generated state, `.terraform`, plans, and the `work/` directory. Never commit a real state file or plan.

## Run the disposable resource and tests

```powershell
terraform init -input=false
terraform validate -no-color
terraform test -no-color
terraform plan -no-color
terraform apply -auto-approve -no-color
terraform state list
terraform state show local_file.marker
terraform state pull | Set-Content -Encoding utf8NoBOM work/state-backup.json
```

The last command assumes PowerShell 7 and creates a local backup that can contain sensitive state values. Keep it in `work/`, which is ignored by Git. Inspect the exact lab root and existing local state before running the apply; this root is disposable and its manual exercise updates local Terraform state.

## Observe genuine local state-lock contention

1. In terminal A, run `terraform apply -auto-approve -no-color -var hold_lock=true`. The opt-in local provisioner waits on a local named pipe while Terraform is still executing the apply and holding the local backend lock.
2. While terminal A is paused, in terminal B at the same lab directory run `terraform plan -no-color -lock-timeout=0s -var hold_lock=true`. Confirm Terraform itself rejects the operation because the state is locked. Save the actual terminal output as evidence; a diagram, fabricated line, or an unrelated process lock is not evidence.
3. After observing the actual refusal, run `python scripts/release_state_lock.py` from terminal B. Confirm the first apply completes and releases its lock. Then run `terraform apply -auto-approve -no-color -var hold_lock=false` to remove the temporary `terraform_data.lock_holder` entry from state.

Do not use `-lock=false` or `force-unlock` to make this exercise pass. The local named-pipe gate keeps one actual Terraform operation in flight on Windows; the Unix version uses a local domain socket. The competing operation and refusal are both Terraform CLI processes against the same state. Run `python scripts/verify_lab.py` to reproduce lifecycle, import, lock contention, drift, configuration rollback, and State recovery in a fresh temporary copy of the lab. The script bounds each Terraform command and the total runtime, suppresses raw State output, and removes its temporary State and marker even if a check fails; it does not touch this checkout's current `terraform.tfstate` or `work/` evidence.

## Import and configuration rollback

The automated import case runs the real Terraform CLI `import` command against the built-in `terraform_data.imported[0]` resource with the synthetic ID `synthetic-existing-state-id`, then checks that the plan is empty and removes only the State address. The `terraform_data` importer is local and state-only: it has no cloud or external object. The pinned `hashicorp/local` provider does not implement import for `local_file`, so this exercise does not claim to import a real Azure resource. For an Azure import, use that resource type's documented ID format, confirm the provider supports import, read the current object, and reconcile HCL before applying.

The rollback case edits only the script's isolated copy of `main.tf`, changes the declared marker content, plans and applies that value, restores the original HCL bytes, and produces a second plan/apply to return the file to the prior declaration. It demonstrates configuration reconciliation, not an undo of external side effects or an Azure resource rollback.

## Observe drift and corrective reconciliation

1. Change only the disposable file `work/managed-marker.txt` to `managed=outside-change` with a text editor.
2. Run `terraform plan -no-color -detailed-exitcode`. Exit code `2` means a successful plan with a non-empty diff. On the recorded Windows run with local provider 2.9.1, the provider reports this content-addressed `local_file` as absent and the plan proposes `+ create`; do not generalize this provider behavior to AzureRM or to every Terraform resource.
3. To inspect the alternative, run `terraform plan -no-color -refresh-only`. In this local provider run, refresh-only reports the binding as deleted. Applying it removes the resource from State but leaves the file untouched. A subsequent normal plan proposes `+ create`; review and apply it to restore the declared bytes. For a resource whose provider exposes changed attributes, refresh-only can instead record those observed attributes in State.
4. For this lab, run `terraform apply -auto-approve -no-color` and verify the file again contains `managed=terraform`.

The file is a genuine local provider-managed object, so this verifies actual local-provider refresh and plan behavior. It does not establish AzureRM drift behavior or Azure Storage backend semantics.

## State recovery and cleanup

Use `terraform state pull` to capture a protected backup before any repair. Inspect the state `lineage` and `serial`, confirm the exact backend/key, stop concurrent writers, and use a dedicated recovery copy or a reviewed Azure Blob version restore procedure. `terraform state push` can overwrite state and must be an exceptional reviewed recovery action; do not use `-force` in this lab. The lab does not restore an Azure Blob version.

After retaining the outputs you need, run `terraform destroy -auto-approve -no-color`. This deletes only the disposable local file resource and state binding. Remove `work/` only after confirming it contains no evidence you need.
