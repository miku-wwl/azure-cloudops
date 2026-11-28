# E8 — Mandatory local incident experiments

**Status:** Complete, first clean cycle executed 2026-11-27. All eight required local scenarios produced an observed failure, a discriminating root-cause signal, same-probe recovery, and run-owned cleanup. Full machine-readable evidence is under [`incidents/evidence/`](../../incidents/evidence); the reusable runners and boundaries are documented in [`incidents/local/README.md`](../../incidents/local/README.md).

## Execution results

| ID | Observed fault and root cause | Recovery and cleanup | Evidence |
|---|---|---|---|
| IR-01 | An explicit loopback DNS wire query returned NXDOMAIN for the synthetic app name; the app probe made no TCP connection during the fault. | The same query returned `127.0.0.1` and the same HTTP health request returned 200. Both listeners and worker threads closed. | [`IR-01_local-dns.json`](../../incidents/evidence/IR-01_local-dns.json) |
| IR-02 | A real health listener passed in an isolated `--network none` container. An exact loopback TCP REJECT rule caused curl failure; the namespace-local rule counter incremented once. | Removing only that rule restored HTTP 200. The negative-control port remained unreachable. The unique container, veth pair and rules disappeared with it. | [`IR-02_local-filter.json`](../../incidents/evidence/IR-02_local-filter.json) |
| IR-05 | UID/GID 65534 read the granted synthetic file but could not write it or read its neighboring control. Removing the group read bit produced a kernel `Permission denied` on the existing path. | Granting only group read restored the same read and the expected SHA-256; write and neighbor controls remained denied. The disposable networkless container was removed. | [`IR-05_local-permissions.json`](../../incidents/evidence/IR-05_local-permissions.json) |
| IR-07 | A unique, disposable kind cluster produced real kubelet `ErrImagePull` and `ImagePullBackOff` state/events for a missing manifest. The node's loopback-only Registry API fixture recorded an HTTP 404 `MANIFEST_UNKNOWN`. | A preloaded scratch image became Ready and passed the same `/health` HTTP probe. The namespace, cluster, unique image, kubeconfig and build context were removed; the pre-existing `argo-canary-local` cluster remained present. | [`IR-07_local-kind.json`](../../incidents/evidence/IR-07_local-kind.json) |
| IR-08 | While a first local Terraform apply held the real local-backend lock, a competing state-changing apply failed with Terraform's actual state-lock error. A separate out-of-band edit produced a provider-observed `local_file` drift plan. | Releasing the owner allowed a retry; Terraform reconciled the file and the final plan had no changes. Destroy and temporary-copy cleanup passed. Azure calls: none. | [`IR-08_local-terraform.txt`](../../incidents/evidence/IR-08_local-terraform.txt) |
| IR-10 | Real loopback requests recorded two HTTP 503 responses. A threshold of 99 missed both; changing only the threshold to 2 fired from the same event IDs. | Restoring the service and issuing the same two HTTP probes yielded 200s and a resolved state. All alert transitions reference measured telemetry IDs; temporary data and listener were removed. | [`IR-10_local-alert.json`](../../incidents/evidence/IR-10_local-alert.json) |
| IR-11 | The stable functional URL returned an actual HTTP 500 from immutable release `v2`; the active pointer and artifact checksum identified the bad release. | An atomic pointer restore to immutable `v1` made the identical request return the expected body and 200. Server and temporary releases were removed. | [`IR-11_local-rollback.json`](../../incidents/evidence/IR-11_local-rollback.json) |
| IR-12 | One synthetic source record was deleted after a complete SHA-256/byte-count manifest and backup were verified; a source read failed before recovery. | The record was restored into a new directory and matched its original digest and value. The full three-object fixture validated and temporary paths were removed. | [`IR-12_local-restore.json`](../../incidents/evidence/IR-12_local-restore.json) |

## What this verifies

- The failures above are observed local process, kernel, Terraform, or Kubernetes outcomes—not handwritten events or synthetic status claims.
- Docker Desktop's Linux engine, kind 0.33.0, the locally cached node image, Terraform 1.15.5 and the repository's `hashicorp/local` provider were sufficient for the stated local scopes.
- No user/default Kubernetes context was used for the kind experiment. The only run-owned cluster was named uniquely and deleted after evidence capture.
- The network-rule and permission experiments ran inside isolated containers. The Terraform scenario ran in the verifier's fresh temporary checkout; the existing lab State was not opened or written.
- For publication, the Windows user-profile prefix in two captured local Terraform temporary paths is replaced with `[LOCAL_TEMP_REDACTED]`; command results and resource values are unchanged.

## What still requires Azure validation

These local outcomes do not validate Azure Private DNS, effective NSGs, managed identity tokens/RBAC, AKS/ACR authentication, Azure Blob State locks, Azure Monitor alert delivery, App Service/Container Apps rollback, or Azure Backup/Storage recovery. IR-07 uses a local Distribution API fixture and does not claim ACR behavior. Azure execution, Azure cost and billing remain separate gates.

No Azure sign-in, subscription/resource query, resource mutation, Azure DevOps operation, or billing query occurred during E8. The Azure cumulative expenditure ceiling remains USD 1.00, with a USD 0.70 planning threshold and USD 0.30 contingency; actual billed spend remains `NOT_VERIFIED`.

Docker Desktop was started for the authorized local experiments and remains running because the pre-existing `argo-canary-local` cluster is present. The E8 cluster and containers were removed; that shared cluster was not modified.
