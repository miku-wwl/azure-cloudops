# Live lab index

The [E9 live-lab catalogue](LIVE_LAB_CATALOGUE.md) contains the required per-lab architecture, permissions, region/SKU, Terraform coverage, cost status, runtime, probes, recovery, teardown, residual checks and delayed-billing checks.

Stage 3 L0 read-only preflight is complete. It found no existing project lab network or App Service resources. The one authorized LAB-IR-11 attempt ended at plan OS verification and both temporary resources were removed. [L0 evidence](L0_READ_ONLY_PREFLIGHT.md) and [LAB-IR-11 Azure evidence](incidents/evidence/IR-11_azure-2026-11-28.md).

| Incident | Local evidence | Final Azure state | Reason or outcome |
|---|---|---|---|
| IR-01 | `LOCAL_VERIFIED` | `BUDGET_DEFERRED` | Private DNS, endpoint and traffic cost gate open. |
| IR-02 | `LOCAL_VERIFIED` | `PERMISSION_DEFERRED` | Requires an existing, approved lab network scope. |
| IR-03 | `DESIGNED` | `PERMISSION_DEFERRED` | Requires an existing, approved lab route-table scope. |
| IR-04 | `DESIGNED` | `BUDGET_DEFERRED` | Peering, probe and traffic cost gate open. |
| IR-05 | `LOCAL_VERIFIED` | `PERMISSION_DEFERRED` | Narrow identity and data-plane scope required. |
| IR-06 | `DESIGNED` | `BUDGET_DEFERRED` | Vault, transactions and private connectivity not costed for this budget. |
| IR-07 | `LOCAL_VERIFIED` | `BUDGET_DEFERRED` | AKS capacity, ACR and traffic cost gate open. |
| IR-08 | `LOCAL_VERIFIED` | `BUDGET_DEFERRED` | Azure Storage transactions and state retention pricing incomplete. |
| IR-09 | `DESIGNED` | `PERMISSION_DEFERRED` | Dedicated scope and positive authorization to exercise policy deny required. |
| IR-10 | `LOCAL_VERIFIED` | `BUDGET_DEFERRED` | Alert, telemetry ingress and retention cost gate open. |
| IR-11 | `LOCAL_VERIFIED` | `BLOCKED` / `CLEANED_UP` | F1 plan created and removed; effective Linux OS was unverified, so app and functional steps were `NOT_RUN`. |
| IR-12 | `LOCAL_VERIFIED` | `BUDGET_DEFERRED` | Storage, retention, transactions and restore costs not established. |

The eight mandatory local contracts passed E8 and E10. [Local incident evidence](E8_LOCAL_INCIDENTS.md) and [second-cycle replay](E10_INDEPENDENT_REPLAY.md). The project closed at `READ_ONLY_AZURE_VERIFIED`; the authorized F1 provision and cleanup are retained as partial Stage 3 evidence. The exact application sequence and all other live incident runs remain unexecuted. Cost Management yielded no charge records for the scoped run, and billing is `BILLING_PENDING`. [Cost ledger](COST_LEDGER.md).
