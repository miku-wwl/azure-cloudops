# Incident catalogue

The canonical contracts are in [`CONTRACTS.md`](CONTRACTS.md). The twelve IDs are preserved from the approved V3 roadmap and map to their primary technical lectures. `AZ06-02` supplies the incident-command and root-cause integration lens for all twelve. E8 execution evidence is summarized in [`../E8_LOCAL_INCIDENTS.md`](../maintainer/history/E8_LOCAL_INCIDENTS.md), with runnable local harnesses in [`local/README.md`](local/README.md).

| ID | Scenario | Primary lecture mapping | Stage 2 class | Current local evidence | Live Azure |
|---|---|---|---|---|
| IR-01 | Private DNS resolution failure | AZ02-03 | Mandatory local | `LOCAL_VERIFIED`; actual NXDOMAIN and same-probe HTTP recovery | `NOT_RUN` |
| IR-02 | Network filtering / NSG failure | AZ02-02, AZ02-04 | Mandatory local | `LOCAL_VERIFIED`; exact namespace firewall counter and same-probe recovery | `NOT_RUN` |
| IR-03 | Incorrect UDR / next-hop route | AZ02-01 | Design only | `CONTRACTED_NOT_RUN` | `NOT_RUN` |
| IR-04 | VNet peering connectivity | AZ08-01 | Design only | `CONTRACTED_NOT_RUN` | `NOT_RUN` |
| IR-05 | Managed Identity / RBAC denial | AZ03-01, AZ03-02, AZ04-04 | Mandatory local | `LOCAL_VERIFIED`; UID/GID 65534 denied then minimally repaired | `NOT_RUN` |
| IR-06 | Key Vault access failure | AZ03-02, AZ04-04 | Design only | `CONTRACTED_NOT_RUN` | `NOT_RUN` |
| IR-07 | AKS / ACR image-pull failure | AZ04-03, AZ03-02 | Mandatory local | `LOCAL_VERIFIED`; real local kubelet `ErrImagePull`/`ImagePullBackOff` and HTTP 404 fixture | `NOT_RUN` |
| IR-08 | Terraform State lock and drift | AZ07-02, AZ07-01 | Mandatory local | `LOCAL_VERIFIED`; competing state-changing apply, real lock refusal and drift repair | `NOT_RUN` |
| IR-09 | Azure Policy deployment denial | AZ03-03, AZ07-01 | Design only | `CONTRACTED_NOT_RUN` | `NOT_RUN` |
| IR-10 | Monitoring and alert failure | AZ05-01, AZ05-02 | Mandatory local | `LOCAL_VERIFIED`; real telemetry, broken-rule detection and recovery | `NOT_RUN` |
| IR-11 | Deployment regression and rollback | AZ04-02, AZ07-03 | Mandatory local | `LOCAL_VERIFIED`; actual HTTP 500 and atomic rollback | `BLOCKED` at plan OS verification; `CLEANED_UP` |
| IR-12 | Synthetic data loss and restoration | AZ06-01, AZ04-04 | Mandatory local | `LOCAL_VERIFIED`; pre-loss SHA-256 manifest and separate-path restore | `NOT_RUN` |

E8 evidence closes the eight mandatory local scenarios. IR-07 exercised kubelet events against a local HTTP 404 fixture. The authorized LAB-IR-11 Azure attempt provisioned a dedicated group and F1 plan, then stopped at plan verification and removed both. App release, fault and recovery in Azure remain `NOT_RUN`. Other live runs stayed deferred. [Azure evidence](evidence/IR-11_azure-2026-11-28.md) and [final lab index](../maintainer/history/LIVE_LAB_INDEX.md).
