# E8 local incident runners

These scripts execute the eight mandatory local scenarios from E7. Every scope is run-owned and temporary; the Azure boundary stays `NOT_RUN`.

## Prerequisites

- Windows Python 3.13+, Go, Docker Desktop Linux engine, `kind`, `kubectl`, and Terraform 1.10+.
- A pre-existing local copy of the node image pinned in `run_e8_cycle.py`.
- Enough local CPU/memory for a one-node kind cluster.

The IR-02 and IR-05 containers use `--network none`. IR-07 builds a scratch application image with `--network=none`, creates a uniquely named one-node kind cluster from a locally cached node image, and maps only a synthetic missing-manifest request to a loopback registry fixture inside that node. It never contacts ACR or a public registry. The run-owned cluster, namespace, application image, kubeconfig and build context are removed on completion. Existing kind clusters are not addressed.

## One complete clean execution cycle

From the repository root, run:

```powershell
python textbook/incidents/local/run_e8_cycle.py --label cycle-2
```

The orchestrator builds two static Linux fixture binaries and runs IR-01/02/05/07/10/11/12 plus the local Terraform State/drift verifier for IR-08. It writes one evidence file per scenario and `cycle-summary.json` under `textbook/incidents/evidence/cycle-2/`. Each run has bounded command timeouts and must pass its checks and cleanup assertions.

To run one scenario alone, invoke the matching `irNN_*.py` script. The scripts accept `--evidence`; IR-02 and IR-05 also require the pinned `--image` argument, and IR-07 requires the pinned node image plus static Linux binaries.

## Evidence boundaries

- IR-01 speaks DNS wire protocol to a run-owned loopback resolver and confirms a real NXDOMAIN before a same-probe HTTP recovery.
- IR-02 creates a veth pair and changes only an exact loopback firewall rule in a disposable network namespace. The local negative control is a port with no listener.
- IR-05 runs as UID/GID 65534 inside a networkless disposable container. Only group-read permission is repaired; write and neighbor-object probes remain denied.
- IR-07 records real kubelet Pod status/events and a loopback mock-registry HTTP 404. It does not establish ACR authentication, AKS networking or any Azure result.
- IR-08 uses the Terraform lab's fresh temporary copy; the competing operation is an actual state-changing `apply` while another process holds the local backend lock.
- IR-10 alert state derives from actual timestamped HTTP responses written to a temporary telemetry file.
- IR-11 exercises a real HTTP 500 from a deliberately bad immutable release and rolls back using an atomic pointer swap.
- IR-12 restores a deleted synthetic record into a new path and checks the pre-loss SHA-256 manifest.

JSON evidence contains observed request/status/event outputs and cleanup results. Terraform command output is retained as text; local state contents are suppressed. Temporary service data and credentials are not retained.
