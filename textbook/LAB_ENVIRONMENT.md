# Local lab environment inventory

- Checked: 2026-11-26 (Pacific/Auckland), after E8/E10.
- Scope: local tool/version and service status only. No Azure login, subscription query, provider registration, or cloud request was performed.

| Capability | Windows | WSL2 `devops-lab` | Evidence / limit |
|---|---|---|---|
| OS / shell | Windows; PowerShell 7.6.9 | Linux kernel 6.6.114.1; Python shell | WSL distribution listed as WSL2; it was stopped after the bounded probe |
| Python | 3.13.9 | 3.12.3 | Both ran the repository Python suites |
| Terraform | 1.15.5 | Not found | E0 Terraform checks ran on Windows only |
| Azure CLI | 2.86.0 installed | Not found | Windows `az --version` only; `az account`, login and cloud API commands were not run |
| Git | 2.49.0.windows.1 | Not found in checked command path | Repository operations use Windows Git |
| PowerShell | 7.6.9 (`pwsh`) | Not found | E0 Windows harness uses PowerShell; WSL Python runner uses Bash |
| Docker | CLI installed; Engine 29.9.3 (`linux x86_64`) responds | Not found | Docker Desktop remained running for local E8; no Azure resource or network operation |
| Podman | Not found | Not found | No Podman machine or service was started |
| Kubernetes tools | `kubectl` 1.36.1, `kind` 0.33.0, `k3d` 5.9.0 | Not found | E8 created and removed its unique kind cluster; the pre-existing `argo-canary-local` cluster remains and was not changed |
| Azurite | Not found; global npm package list empty | Not found | No package was installed or emulator started |
| Node / npm | Installed | Not found | Not required by the local Python harness |
| Browser automation | Available through Codex tools | Not probed inside WSL | Not required for E2; no browser session used |

## Current consequence

- The safe default is Windows/WSL Python and the already-installed Windows Terraform. The new `labctl.py` harness is standard-library-only and local-only.
- The genuine local Terraform State lab is executable and was verified with Terraform 1.15.5 and `hashicorp/local` 2.9.1. Its cloud-fidelity boundary remains explicit.
- Docker is available now. E8 produced genuine events from its run-owned kind cluster for IR-07; see `E8_LOCAL_INCIDENTS.md`. This local kubelet evidence does not establish AKS or ACR behavior.
- Azurite is optional and not a substitute for Azure Storage or Azure Blob lease validation. It will not be installed unless a specific local experiment needs it.

Earlier E2/E7 host-capability statements are point-in-time snapshots; they correctly describe Docker as unavailable then. The later E8 recheck supersedes those statements for current work.
