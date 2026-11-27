# E10 — Independent clean execution replay

**Status:** `LOCAL_VERIFIED` on 2026-11-27. Two complete cycles each ran all eight mandatory local incidents and passed their evidence and cleanup checks. Machine-readable verification is in [`incidents/evidence/e10-verification.json`](incidents/evidence/e10-verification.json).

## Cycle evidence

| Cycle | Result | Execution |
|---|---|---|
| [`cycle-1`](incidents/evidence/cycle-1/cycle-summary.json) | 8/8 `LOCAL_VERIFIED`; cleanup checks pass | The first E8 run. Each scenario ran as a separate process in its own loopback listener, networkless Docker container, unique kind cluster, Terraform temporary copy, or temporary data directory. Its scenario evidence remains linked from the cycle summary. |
| [`cycle-2`](incidents/evidence/cycle-2/cycle-summary.json) | 8/8 `LOCAL_VERIFIED`; cleanup checks pass; 141.026 seconds | A separate invocation of [`run_e8_cycle.py`](incidents/local/run_e8_cycle.py) rebuilt both local Linux fixtures, ran every mandatory scenario serially, checked resource teardown and verified the existing Terraform source and State hashes were unchanged. |

## Independent scenario replays

- **Network — IR-02:** A new Docker network namespace and veth pair were created. The exact local firewall rule again produced one measured counter hit, the allowed service recovered after removing only that rule, and the negative control remained unreachable. The second container name differs from cycle 1.
- **Identity/authorization — IR-05:** A fresh disposable Linux container ran the same object-read as UID/GID 65534. Permission removal produced actual `Permission denied`; group-read-only repair restored the digest while write and neighbor reads remained denied. The second container name differs from cycle 1.
- **Data recovery — IR-12:** A new synthetic data directory, backup and restore path were created. The same three-object manifest SHA-256 reproduced, source loss was observed before restore, and the separate-path copy validated again.

IR-07 also used a newly named kind cluster and unique application image in cycle 2. Its actual Pod status, Warning events, loopback registry HTTP 404, successful same-probe recovery and resource cleanup are retained separately under `incidents/evidence/cycle-2/`.

This is an independent execution replay in fresh local process/resource scopes, not a separate human reviewer. Both cycles are local-only; no Azure authentication, resource query/mutation, Azure DevOps operation or billing query occurred. Local success does not establish Azure service behavior or actual billed spend.

## Reproduction

```powershell
python textbook/incidents/local/run_e8_cycle.py --label cycle-3
python textbook/incidents/local/verify_e10.py
```

The cycle runner refuses to overwrite an existing evidence directory. Run the verifier only after at least two complete cycle summaries and the corresponding first-cycle incident evidence exist.
