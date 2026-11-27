# E2 local lab substrate acceptance

- Date: 2026-11-27 (Pacific/Auckland).
- Status: ACCEPTED for the local-only reusable command/test substrate.
- Scope: host capability inventory, repository-wide bounded Python runner, deterministic local lifecycle smoke, and cleanup safety.
- Cloud boundary: no Azure sign-in, subscription/billing query, provider registration, resource operation, or network request was performed.

## Host inventory

See [`LAB_ENVIRONMENT.md`](LAB_ENVIRONMENT.md) for command-level results. Windows provides Python 3.13.9, Terraform 1.15.5, Azure CLI 2.86.0, Git 2.49.0, PowerShell 7.6.9 and the `kubectl`/`kind`/`k3d` clients. The Docker CLI cannot connect to Docker Desktop's Linux Engine; Podman and Azurite are absent. The `devops-lab` WSL2 distribution has Python 3.12.3 but no Terraform, Azure CLI, Docker/Podman, Kubernetes clients, Git or Azurite in the checked command path. It returned to `Stopped` after the read-only inspection.

No tool was installed, no cluster/emulator/service was started, and no long-running local process was left running. `az --version` only reported its version. No `az login` or `az account` command was run.

## Implemented commands and safety

`textbook/tools/labctl.py` implements the requested local command lifecycle:

- `preflight`
- `setup`
- `baseline`
- `test`
- `inject`
- `diagnose`
- `recover`
- `reset`
- `teardown`
- `residual`

Each command requires `--target-scope local`; `azure` and other scopes are rejected. `setup` creates a unique direct-child run directory under the system temporary directory and prints its run ID/path. It writes a deterministic two-file synthetic fixture only. The tool has no network, Azure SDK/CLI call or child process. JSON input is capped at 16 KiB and directory inspection at eight entries. Path validation rejects symlinks/reparse points and paths outside the tool-owned temporary root. Teardown requires the exact run ID, known files and a healthy/reset fixture; it unlinks those two files and removes only the empty run directory. Unknown files are listed and preserved. CLI exit code 4 signals an invalid scope/ownership/state; code 5 signals failed local verification or bounded residual inspection.

`textbook/tools/test_python.py` now discovers chapter and shared `tools/tests` suites, starts one Python process per directory, rejects zero-test discovery, and applies a 300-second timeout to each process. `test_all.sh --python` calls that same cross-platform runner. This closes the previous gap where shared tests were not included.

## Verification

| Check | Result | Evidence limit |
|---|---|---|
| Windows test runner | PASS — 418 tests, 23 directories, zero failed directories | Python unit suites only |
| WSL test runner | PASS — 418 tests, 23 directories, zero failed directories | Python unit suites only |
| `bash -n textbook/tools/test_all.sh` | PASS | Shell syntax only |
| Windows `labctl preflight` | PASS — local Python/repository detected; optional-tool presence reported | Deliberately does not inspect Azure authentication |
| Manual lifecycle | PASS — setup, healthy baseline/test, injected synthetic fixture failure, diagnosis, recovery with same synthetic probe, reset, residual scan, teardown and post-teardown residual scan | `SMOKE-LOCAL` is not a network/service incident and not one of the eight mandatory incidents |
| Local run directory | Removed by exact run ID; post-teardown residual result `run_dir_exists=false` | No repository working files or ignored State were involved |

The shared runner discovered 23 test directories: the original 22 chapter directories plus `tools/tests`. The one new shared test module exercises scope rejection, state transitions, path escape/symlink refusal, unexpected-file preservation, bounded residual listing and exact-run-ID teardown.

## Limits carried forward

- Actual Kubernetes image-pull events cannot be produced until a working local container engine is available. E2 intentionally did not start Docker Desktop or create a cluster; recheck that prerequisite during IR-07 and do not fabricate output.
- No Azurite/Storage emulator is installed. It is optional and would not prove Azure Blob lease or service behavior.
- The smoke fixture is a harness validation only. It does not count as any IR-01/02/05/07/08/10/11/12 acceptance.
- Terraform local locking/drift remains the genuine local evidence recorded in the E0 and AZ07-02 acceptance reports. No Azure Blob backend has been initialized.
- Stage 2 is still prohibited from creating or changing Azure resources. Actual project spend remains `NOT_VERIFIED`; the USD 1.00 cumulative ceiling and USD 0.70 planning threshold remain unchanged.
