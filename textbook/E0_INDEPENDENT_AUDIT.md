# E0 independent audit — Stage 1 source and evidence review

- Audit date: 2026-11-27 (Pacific/Auckland).
- Repository: `D:/workshop/nov/azure-cloudops`.
- Branch and starting revision: `main`, `d1437a7320c74498f38c9e20d49cad4a2c5248b7` (same as `origin/main` when the audit began).
- Scope: Stage 1 chapters, source map, acceptance records, local experiments, Terraform roots, live-read-only runbooks, tests, validation claims, publication outputs and safety/cleanup instructions.
- Cloud boundary: Stage 2 remains local/offline. No Azure sign-in, subscription selection, Azure CLI request, Cost Management query, resource operation, provider registration or deployment was performed.

## Audit method

The audit checked the 23-chapter inventory against chapter acceptance records, the source map, verification matrix and built PDFs. It re-ran the complete Python test set independently on Windows and WSL after corrections, exercised the Terraform State lab in an isolated temporary checkout, reviewed the three rebuilt affected PDFs page by page, and checked high-risk technical assertions against current Microsoft primary sources. Earlier Stage 1 results remain historical evidence; this report records only checks repeated during E0.

The review focused on executable contracts, destructive or cloud-touching paths, cost arithmetic, routing decisions, Terraform state handling, documentation/source alignment, and whether recorded evidence exceeded what was actually run. It did not turn local fixtures into Azure evidence.

## Findings and corrections

### FIN-01 shared-cost cent reconciliation

- Finding: each cost-center share was independently rounded to cents. A one-cent shared pool at equal weights produced zero cents total; other fractional splits could create or lose cents.
- Correction: allocate integer cents by deterministic largest remainder, with stable cost-center ordering for tied remainders. Reject unknown cost-center keys. Added regression cases for one-cent and two-cent pools.
- Verification: FIN-01 now passes 29 unit tests on Windows Python 3.13.9 and in WSL; the full suite passes on both systems (407 tests across 22 directories).
- Scope limit: this is an offline allocation model. It is not a Cost Management parser or an Azure billing query.

### AZ02-01 route contract accepted invalid combinations

- Finding: `Route.from_dict` accepted an unknown/misspelled next-hop type such as `VirtualApppliance`; it also accepted a next-hop IP on non-appliance routes and relied on manual fixture tagging for special next-hop types.
- Correction: validate the supported next-hop enum, require the appliance IP only for `VirtualAppliance`, infer the known special route kinds, and fail closed for unsupported combinations. Added three negative tests.
- Verification: the local suite now passes 16 tests on Windows and WSL; the full suite passes as stated above.
- Scope limit: this remains a deliberately small IPv4 route-selection and path hypothesis model. It does not call Azure, query NIC effective routes, model every special route rule, establish packet delivery, or prove an NVA return path.

### AZ07-02 local State verification had unsafe workspace behavior

- Finding: the previous verifier ran against checkout-relative files, could leave raw State in ignored output/logs, risked overwriting pre-existing State, and did not consistently bound subprocess time or clean up a held lock after failure. The Unix lock helper could unlink a pre-existing socket path.
- Correction: copy the lab to a fresh system temporary directory; refuse to reuse an existing Unix socket; bound command duration; suppress raw State output; release/terminate/kill the lock holder in failure paths; and remove only the owned temporary directory. Updated instructions to use PowerShell 7 UTF-8 without BOM and state the disposable-State / Python 3.10+ requirements.
- Verification: ran the complete lab on Windows with Terraform 1.15.5 and `hashicorp/local` 2.9.1. It demonstrated actual lock refusal, local-file drift detection/reconciliation, State pull/push recovery, a no-diff plan and destroy; the temporary directory was removed. The verifier did not initialize an Azure provider or make an Azure API request. Existing checkout State, user work and evidence were preserved.

### Publication and progress documentation drift

- Finding: the root README still described Stage 1 B5 as in progress and the matrix described B9/package verification as pending, despite the Stage 1 acceptance record.
- The approved roadmap also still described Stage 1 B2 as active and said Stage 2 had not started; its closing instruction applied to the earlier document-only planning change and conflicted with the owner's later master prompt and “start execution” request.
- Correction: synchronize the root README, verification matrix, progress report, cost ledger and roadmap to show Stage 1 23/23 and B9 accepted, Stage 2 E0 complete/E1 current, and cloud mutation limits. The roadmap now treats its old handoff sentence as superseded by this later authorization, while preserving the per-experiment Stage 3 authorization/cost gate. Hosted CI/secret scan remain clearly outstanding.
- Kept the old 402-test counts as historical Stage 1 evidence and added this E0 delta.
- Verification: rebuilt AZ02-01 (8 pages), FIN-01 (9 pages) and AZ07-02 (7 pages); rendered all 24 pages as page-pair sheets and visually checked them for clipping, overlap, broken code wrapping, damaged figures, page-number errors and reference/layout defects. No such defect was found. The updated PDFs are in `textbook/dist/pdf/`.

## Source-backed claims and unresolved conflict

- Azure route selection is described as longest-prefix-first; the next-hop REST vocabulary and UDR behavior are linked to the current Microsoft Learn and REST documentation in `SOURCE_MAP.md`. The corrected fixture now rejects misspelled next-hop enum values rather than silently accepting them.
- Current Azure Monitor Activity Log schema documentation supports the narrow point that some authentication/authorization failures before an operation are not represented as Activity Log operation events. The chapters do not treat Activity Log as a complete security audit feed.
- The Private DNS NXDOMAIN and Load Balancer probe explanations were checked against Microsoft Learn; they remain scoped to the documented conditions and do not claim that probe success proves application correctness.
- The reservation exchange policy shown in FIN-01 is a future policy effective 2027-02-01; current Microsoft documentation states the change. It is dated for revalidation and is not represented as effective on this audit date.
- AZ04-01 retains a visible unresolved Microsoft documentation conflict: the VM Scale Set upgrade-policy page describes policy modes for Flexible orchestration, while the orchestration-mode page says the upgrade-policy parameter must be null/empty for Flexible. The audit did not silently choose one page or expand the synthetic model into an Azure guarantee. Recheck the official pages before any live experiment.

Primary sources reviewed:

- [Azure virtual network traffic routing](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview)
- [Azure Routes GET REST schema](https://learn.microsoft.com/en-us/rest/api/virtualnetwork/routes/get?view=rest-virtualnetwork-2026-01-01)
- [Activity Log event schema](https://learn.microsoft.com/en-us/azure/azure-monitor/platform/activity-log-schema) and [Azure Activity Log](https://learn.microsoft.com/en-us/azure/azure-monitor/platform/activity-log)
- [Troubleshoot NXDOMAIN from Private DNS](https://learn.microsoft.com/en-us/troubleshoot/azure/dns/troubleshoot-private-dns-zone-override-nxdomain)
- [Azure Load Balancer probe overview](https://learn.microsoft.com/en-us/azure/load-balancer/load-balancer-custom-probe-overview)
- [VMSS upgrade policy](https://learn.microsoft.com/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-upgrade-policy) and [VMSS orchestration modes](https://learn.microsoft.com/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-orchestration-modes)
- [Changes to the Azure reservation exchange policy](https://learn.microsoft.com/en-us/azure/cost-management-billing/reservations/reservation-exchange-policy-changes)

## Re-run evidence

| Check | Result | Boundary |
|---|---|---|
| Windows Python suite | PASS — 407 tests, 22 directories, zero failed directories | Python fixtures and local tools only |
| WSL Python suite (`devops-lab`) | PASS — 407 tests, 22 directories, zero failed directories | Independent OS/runtime; no Azure interaction |
| AZ02-01 focused suite | PASS — 16 tests | Synthetic route model only |
| FIN-01 focused suite | PASS — 29 tests | Fictional ledger only |
| AZ07-02 State verifier | PASS — lock contention, local drift and State recovery flow | Isolated temp checkout, local provider, no Azure backend |
| Affected PDF review | PASS — all 24 pages visually inspected | AZ02-01: 8; FIN-01: 9; AZ07-02: 7 |

## Outstanding items carried forward

- No `.github/workflows` CI workflow existed at audit start. The Stage 1 B9 record did not claim hosted CI, PDF/UA conformance or a configured secret scan. These remain required for the master Milestone A and will be implemented and verified in the engineering gates; they are not silently credited to B9.
- The package ZIPs must be rebuilt and byte-verified against the corrected sources and final PDFs before the next publication acceptance.
- Docker Desktop's Linux engine was unavailable in the earlier host check; local Kubernetes validation cannot be claimed until that prerequisite is rechecked. Azure CLI availability does not establish Azure authorization, and no Azure CLI command was run.
- Live Azure authorization, exact target scope, regional SKU availability, and reliably estimated incremental cost remain unchecked. Actual cumulative spend remains `NOT_VERIFIED`; the USD 1.00 cumulative ceiling and USD 0.70 planning threshold remain in force.

## E0 disposition

The identified reproducible defects have been corrected and the affected tests and PDFs pass their current checks. E0 audit evidence is complete for these findings. The hosted CI/security gate, final package refresh and Stage 2 engineering acceptance remain open; this disposition does not declare `TEXTBOOK_V1_RELEASE_READY`, `LIVE_LAB_READY` or any Azure live milestone.
