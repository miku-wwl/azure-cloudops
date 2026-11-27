# Incident catalogue

The canonical E7 contracts are in [`CONTRACTS.md`](CONTRACTS.md). The twelve IDs are preserved from the approved V3 roadmap and map to their primary technical lectures. `AZ06-02` supplies the incident-command and root-cause integration lens for all twelve.

| ID | Scenario | Primary lecture mapping | Stage 2 class | E7 status |
|---|---|---|---|---|
| IR-01 | Private DNS resolution failure | AZ02-03 | Mandatory local | Contracted; E8 run not started |
| IR-02 | Network filtering / NSG failure | AZ02-02, AZ02-04 | Mandatory local | Contracted; E8 run not started |
| IR-03 | Incorrect UDR / next-hop route | AZ02-01 | Design only | Contracted; not run |
| IR-04 | VNet peering connectivity | AZ08-01 | Design only | Contracted; not run |
| IR-05 | Managed Identity / RBAC denial | AZ03-01, AZ03-02, AZ04-04 | Mandatory local | Contracted; E8 run not started |
| IR-06 | Key Vault access failure | AZ03-02, AZ04-04 | Design only | Contracted; not run |
| IR-07 | AKS / ACR image-pull failure | AZ04-03, AZ03-02 | Mandatory local | Contracted; local engine/cluster prerequisite unresolved |
| IR-08 | Terraform State lock and drift | AZ07-02, AZ07-01 | Mandatory local | Contracted; existing E4 local lab evidence is separate from E8 closure |
| IR-09 | Azure Policy deployment denial | AZ03-03, AZ07-01 | Design only | Contracted; not run |
| IR-10 | Monitoring and alert failure | AZ05-01, AZ05-02 | Mandatory local | Contracted; E8 run not started |
| IR-11 | Deployment regression and rollback | AZ04-02, AZ07-03 | Mandatory local | Contracted; E8 run not started |
| IR-12 | Synthetic data loss and restoration | AZ06-01, AZ04-04 | Mandatory local | Contracted; E8 run not started |

E7 contracts are design artifacts; they are not incident-execution records. Only E8 evidence can advance one of the eight mandatory local scenarios. Azure validation stays `NOT_RUN` until its own authorized gate.
