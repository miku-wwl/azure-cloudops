# Azure CloudOps Technical Textbook — Curriculum

Audience: experienced Azure, AWS, Terraform, Kubernetes and software engineers moving into senior Azure infrastructure, platform, DevOps, SRE and cloud-architecture work. Explanations are in Chinese with established English technical terminology. This is a mechanism and operations curriculum, not certification revision.

| No. | Lecture | Core question |
|---:|---|---|
| 01 | AZ00-01 — Azure Landing Zone, ARM and Control Plane | How does an Azure subscription become an enterprise-governed environment? |
| 02 | AZ01-01 — Azure Well-Architected Framework and Reliability | Why does multi-zone deployment not automatically guarantee reliability? |
| 03 | AZ02-01 — VNet, UDR and Effective Routes | Which route wins, and where can asymmetric routing arise? |
| 04 | AZ02-02 — NSG, ASG and Network Diagnostics | Which stateful rule admits or rejects this flow, and how can it be proven? |
| 05 | AZ02-03 — Private DNS, Private Link and Private Endpoint | How does a name resolve to a private endpoint, and which gate can still deny access? |
| 06 | AZ02-04 — Load Balancer, Application Gateway and Front Door | At which layer did health probing or request routing fail? |
| 07 | AZ03-01 — Microsoft Entra ID, Tokens and Azure RBAC | Which identity, audience, action and scope govern this request? |
| 08 | AZ03-02 — Managed Identity, Key Vault and Federation | How does a workload obtain and use a credential without storing one? |
| 09 | AZ03-03 — Azure Policy, Activity Log and Defender for Cloud | Which control prevents, records, evaluates or remediates a configuration? |
| 10 | AZ04-01 — VM, VMSS, Managed Disk and Operations | Which VM lifecycle and dependency state explains the symptom? |
| 11 | AZ04-02 — App Service, Container Apps and Deployment | How do slots, revisions, probes and rollback affect a live release? |
| 12 | AZ04-03 — Azure Kubernetes Service and Azure Container Registry | Which identity, network or scheduling boundary prevented the workload becoming ready? |
| 13 | AZ04-04 — Azure Storage and Azure SQL | Which network, identity and data-protection boundaries govern a read or restore? |
| 14 | AZ05-01 — Azure Monitor, Metrics and Alerts | How do dimensions, aggregation and evaluation windows produce an alert state? |
| 15 | AZ05-02 — Log Analytics, KQL and Application Insights | How can telemetry schema and correlation expose a distributed failure? |
| 16 | AZ05-03 — Azure CLI, PowerShell and Resource Graph | How can an operator inventory resources safely, completely and repeatably? |
| 17 | AZ06-01 — Azure Backup, Restore and Site Recovery | How do recovery points, integrity checks and RPO/RTO shape a real recovery? |
| 18 | AZ06-02 — Incident Response, RCA and Integrated Banking Case | How do evidence, competing hypotheses and bounded repair converge on a defensible RCA? |
| 19 | AZ07-01 — Terraform, AzureRM, AzAPI and Modules | Which layer owns each operation and how does Terraform build its graph? |
| 20 | AZ07-02 — Azure Remote State, Locking and Drift | What does the blob lease protect, and how is state drift detected and recovered? |
| 21 | AZ07-03 — Azure DevOps, Pipelines and Workload Identity Federation | How can an exact plan move through a trusted approval boundary? |
| 22 | AZ08-01 — Hub-Spoke, VPN, ExpressRoute and Enterprise DNS | Which routing, BGP and DNS boundaries connect hybrid networks? |
| 23 | FIN-01 — Azure FinOps and Resource Cost Recovery | How can gross charges, credits, retained resources and teardown be reconciled? |

Each lecture follows the learning progression: engineering scenario, mechanism, original figure, worked example, reproducible experiment, fault analysis, exercises with detailed solutions, and primary references. A local experiment is explicitly distinguished from Azure service verification.
