# Live lab index

No Azure resources have been created or modified for this project. The entries below are curriculum contracts from the approved V3 roadmap; they are not executed experiments. Azure-specific validation remains NOT_RUN until Stage 3 authorization and cost gates pass.

| ID | Scenario | Local requirement | Live Azure mapping | Current state |
|---|---|---|---|---|
| IR-01 | Private DNS resolution | Mandatory local mechanism | Private DNS zone/link and Private Endpoint | PLANNED |
| IR-02 | Network filtering / NSG | Mandatory local mechanism | NSG and Network Watcher | PLANNED |
| IR-03 | UDR / route failure | Design contract | Azure route table and Next Hop | PLANNED |
| IR-04 | Peering connectivity | Design contract | VNet peering and effective routes | PLANNED |
| IR-05 | Identity permission denied | Mandatory local mechanism | Managed Identity plus Storage or Key Vault data-plane RBAC | PLANNED |
| IR-06 | Key Vault access failure | Design contract | Key Vault network, token audience and data permissions | PLANNED |
| IR-07 | Image pull failure | Mandatory local Kubernetes mechanism | AKS/ACR identity, network and image pull | PLANNED |
| IR-08 | Terraform state lock / drift | Mandatory genuine local lock and drift evidence | Azure Storage backend and controlled Terraform delivery | PLANNED |
| IR-09 | Azure Policy denial | Design and policy-fixture contract | Temporary, authorized resource-group policy | PLANNED |
| IR-10 | Monitoring / alert failure | Mandatory local signal-to-alert-to-recovery mechanism | Azure Monitor alert and notification path | PLANNED |
| IR-11 | Deployment regression | Mandatory local version rollback | Optional approved Azure deployment and rollback | PLANNED |
| IR-12 | Data loss / restore | Mandatory isolated local checksum-verified restore | Optional Azure Storage recovery | PLANNED |

Mandatory local scenarios: IR-01, IR-02, IR-05, IR-07, IR-08, IR-10, IR-11 and IR-12. No local scenario is marked verified until its actual baseline, injected failure, diagnosis, repair, same-probe recovery and cleanup have been recorded. No live scenario is marked verified from a mock, diagram, plan or local emulator.
