# Local lab environment inventory

- Checked: 2026-11-27 (Pacific/Auckland).
- Scope: local tool/version and service status only. No Azure login, subscription query, provider registration, or cloud request was performed.

| Capability | Windows | WSL2 `devops-lab` | Evidence / limit |
|---|---|---|---|
| OS / shell | Windows; PowerShell 7.6.9 | Linux kernel 6.6.114.1; Python shell | WSL distribution listed as WSL2; it was stopped after the bounded probe |
| Python | 3.13.9 | 3.12.3 | Both ran the repository Python suites |
| Terraform | 1.15.5 | Not found | E0 Terraform checks ran on Windows only |
| Azure CLI | 2.86.0 installed | Not found | Windows `az --version` only; `az account`, login and cloud API commands were not run |
| Git | 2.49.0.windows.1 | Not found in checked command path | Repository operations use Windows Git |
| PowerShell | 7.6.9 (`pwsh`) | Not found | E0 Windows harness uses PowerShell; WSL Python runner uses Bash |
| Docker | CLI installed | Not found | `docker info` failed: `dockerDesktopLinuxEngine` named pipe is absent |
| Podman | Not found | Not found | No Podman machine or service was started |
| Kubernetes tools | `kubectl` 1.36.1, `kind` 0.33.0, `k3d` 5.9.0 | Not found | `kind get clusters` / `k3d cluster list` could not connect to Docker; no cluster was created |
| Azurite | Not found; global npm package list empty | Not found | No package was installed or emulator started |
| Node / npm | Installed | Not found | Not required by the local Python harness |
| Browser automation | Available through Codex tools | Not probed inside WSL | Not required for E2; no browser session used |

## Consequence for E2–E8

- The safe default is Windows/WSL Python and the already-installed Windows Terraform. The new `labctl.py` harness is standard-library-only and local-only.
- The genuine local Terraform State lab is executable and was verified with Terraform 1.15.5 and `hashicorp/local` 2.9.1. Its cloud-fidelity boundary remains explicit.
- Actual Kubernetes event-based image-pull diagnosis is not currently possible because there is no working container engine. Recheck Docker Desktop availability before IR-07; if no engine can be started safely or the user environment blocks it, keep the scenario incomplete rather than fabricate Kubernetes events.
- Azurite is optional and not a substitute for Azure Storage or Azure Blob lease validation. It will not be installed unless a specific local experiment needs it.
