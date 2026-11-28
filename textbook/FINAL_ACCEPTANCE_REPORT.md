# Azure CloudOps V1 — final acceptance

- Closure date: 2026-11-28 (Pacific/Auckland).
- Repository and branch: `miku-wwl/azure-cloudops`, `main`.
- Scope: Stage 1 and Stage 2 delivery, Stage 3 read-only evidence and one authorized LAB-IR-11 attempt.

## V1.0.1 textbook refinement

The refinement builds on accepted revision `8cdad7fba8db8f821aaf013bd20637441e6c22dc`. It covers the 23 Stage 1 textbooks. Publication now has 200 pages (183 in V1), 95 editable SVG assets (92 placed in the PDFs) and 0 genuine Azure Portal screenshots. The original 95 figure assets remain available; the telemetry architecture diagram was corrected. All 23 PDFs were rebuilt and their final renders and extracted text checked. The [review and R0–R8 matrix](V1_0_1_TEXTBOOK_REVIEW.md) records the per-lecture results, technical corrections and visual checks. The [publication manifest](dist/publication-manifest.json) is the source of truth for exact ZIP sizes, entry lists and SHA-256 digests.

The local release checks passed 534 Python tests, 13 backend-free Terraform tests across three roots, and 6 Pester tests. The publication gate additionally requires the exact pushed revision to pass all five jobs in [GitHub Actions](https://github.com/miku-wwl/azure-cloudops/actions/workflows/ci.yml?query=branch%3Amain).

V1.0.1 has USD 0.00 additional Azure budget and performed no Azure request or mutation. The seven KQL workspace templates are `NOT_RUN`. Azure LAB-IR-11 remains partial; local HTTP rollback has separate evidence. The historical labels below retain their original evidence scopes.

## V1 acceptance history

## Milestones

| Milestone | Result | Evidence |
|---|---|---|
| `TEXTBOOK_V1_RELEASE_READY` | Achieved | 23 Chinese lectures with editable sources and experiments, per-lecture acceptance, 95 original SVG mechanism figures, PDF visual review, verified ZIPs and publication manifest. |
| `LIVE_LAB_READY` | Achieved | E0–E10, three architecture views, six ADRs, Terraform and Azure Pipelines contracts, diagnostic tooling, 12 incident contracts, eight mandatory local closures and independent second-cycle replay. |
| `READ_ONLY_AZURE_VERIFIED` | Achieved | Authorized subscription context, ARM and Resource Graph inventory, governance reads and candidate preflight. [L0 evidence](L0_READ_ONLY_PREFLIGHT.md). |
| `LIVE_VALIDATED_SUBSET` | Outstanding | LAB-IR-11 reached F1 plan provisioning and verified cleanup. The Azure app's functional, failure and recovery steps remain open. |
| `PORTFOLIO_READY_LIVE` | Outstanding | Mandatory live qualifications in the approved V3 roadmap remain open. |

## Publication

The final collection contains 23 independent PDFs, 183 pages, 95 mechanism SVGs and 0 genuine Azure Portal screenshots. V1 rebuilds AZ04-02, AZ05-03, AZ06-02 and FIN-01 from observed evidence. All 30 pages of those four PDFs were rendered at 88 DPI and visually inspected, with the new observation pages also examined at 140 DPI. The other 19 PDFs are byte-identical to the previously reviewed publication at `41532cd`. Every PDF has an outline and readable extractable text. The independent reader or print proof and PDF/UA certification were outside this verification.

| Lecture | Pages | Lecture | Pages | Lecture | Pages |
|---|---:|---|---:|---|---:|
| AZ00-01 | 8 | AZ01-01 | 7 | AZ02-01 | 8 |
| AZ02-02 | 8 | AZ02-03 | 11 | AZ02-04 | 9 |
| AZ03-01 | 9 | AZ03-02 | 9 | AZ03-03 | 8 |
| AZ04-01 | 6 | AZ04-02 | 7 | AZ04-03 | 9 |
| AZ04-04 | 8 | AZ05-01 | 6 | AZ05-02 | 7 |
| AZ05-03 | 7 | AZ06-01 | 7 | AZ06-02 | 7 |
| AZ07-01 | 9 | AZ07-02 | 7 | AZ07-03 | 8 |
| AZ08-01 | 9 | FIN-01 | 9 | **Total** | **183** |

- [PDF ZIP](dist/Azure-CloudOps-PDF.zip) contains exactly 23 PDFs and matches the individual PDFs byte-for-byte.
- [Source ZIP](dist/Azure-CloudOps-Sources.zip) contains 428 files and matches the repository source inventory with LF normalization for text.
- [Publication manifest](dist/publication-manifest.json) records the exact byte sizes, SHA-256 hashes and per-entry SHA-256 hashes for both ZIPs. It is stored outside the ZIPs.

## Final verification

| Area | Observed result |
|---|---|
| Python | Windows Python 3.13.9 reported 534 tests in 24 directories and zero failed directories. Includes the 12-contract matrix, control and rejection cases, Resource Graph fallback, and 19 IR-11 package and watchdog tests. |
| Terraform | Terraform 1.15.5 passed recursive format, backend-free init, validate and all 13 plan/mock runs across three test roots. The AzureRM/AzAPI root contributes eight mock runs. Real Azure deployment, remote state and cloud identity remain separate gates. |
| PowerShell | Pester 5.7.1 passed 6/6 parser and tooling contract tests, including the positive ARM Linux evidence requirement before app creation. |
| Replay | The E10 verifier regenerated the two-cycle result in a scratch copy. Its output matched the preserved evidence after LF normalization. Network, permission and data recovery replays used distinct run contexts. This was a verification of existing evidence. |
| Publication | Curriculum, source map, local Markdown links, E9's 13 complete cards, PDF payloads and archive manifest verified. The four lecture acceptance addenda record the rebuilt artifacts. |
| GitHub | [Offline engineering acceptance](https://github.com/miku-wwl/azure-cloudops/actions/workflows/ci.yml) checks exact revisions with Windows and Ubuntu Python/package jobs, Terraform, Pester and Gitleaks. The exact closure commit and its run are linked in the delivery report. The starting revision `41532cdb607051b058d6665f4afbc4f0af4418c2` passed [run 46071201359](https://github.com/miku-wwl/azure-cloudops/actions/runs/46071201359). |

The architecture contracts and replay evidence are preserved in [E1 architecture](architecture/README.md), [E8 local execution](E8_LOCAL_INCIDENTS.md) and [E10 independent replay](E10_INDEPENDENT_REPLAY.md). Controlled-delivery negative cases preserve exact-plan scope and one-use approval boundaries. Azure DevOps server enforcement, WIF identity exchange, Azure Blob locking and enterprise live fidelity remain outside the observed runs.

The [first closure CI run](https://github.com/miku-wwl/azure-cloudops/actions/runs/46077725264) flagged ten values in the original publication manifest as generic API keys. Every value matched the recomputed SHA-256 of its ZIP entry. The final manifest gives paths and digests separate fields. A separate full history scan of `main` identified one old prose match for `regional/SKU`. The `.gitleaksignore` file records these eleven verified historical fingerprints. The local history scan and the hosted push revision scan use the default detection rules.

## Stage 3 outcome

L0 used the existing default Azure for Students CLI context. The Resource Graph extension install failed locally and the inventory tool used the official REST query transport. It returned one complete page of three Network Watcher resources within the approved subscription. ARM inventory agreed. Azure governance and cost reads are recorded with separate evidence limits. The owner skipped the interactive KQL demo sign-in. All seven AZ05-02 templates retain their documented execution instructions and `NOT_RUN` state. [L0 preflight](L0_READ_ONLY_PREFLIGHT.md).

The authorized scope was `rg-azure-cloudops-ir11-aue`, `asp-azure-cloudops-ir11-aue` (Linux F1 requested), and `azcoir11aue261126` (Node 24 LTS) in Australia East for up to 45 minutes including cleanup. Azure Activity Log confirmed the resource group and F1 plan writes. The runbook verified the plan name, region and F1/Free SKU before a missing top-level `reserved` field stopped effective Linux verification. The Web App, ZIP uploads, baseline, intentional HTTP 500 and recovery were `NOT_RUN` in Azure. [Sanitized run evidence](incidents/evidence/IR-11_azure-2026-11-28.md).

The plan and group were deleted. Primary verification found zero residual resources in 125.9 seconds from the first write request. The independent watchdog reported `CLEANED_UP`, and the unrelated subscription inventory matched preflight. The runbook now reads `properties.reserved` through the documented ARM API and fails closed unless it is boolean true. The ARM projection change passed the local checks. The failure stop condition ended the authorized cloud run.

Local validation of the two Node ZIPs observed 200 → 500 → 200, with the expected release and response body at each step. The recorded original ZIP SHA-256 is `55604247FAF289CF1AFDD5CE25EC4E3C865165D3E0B91A6E0B834CA02A135C38`.

## All incident results

| ID | Local outcome | Azure outcome |
|---|---|---|
| IR-01 | `LOCAL_VERIFIED`. NXDOMAIN, then same DNS and HTTP 200 recovery. | `BUDGET_DEFERRED`. Private DNS, endpoint and traffic cost gate open. |
| IR-02 | `LOCAL_VERIFIED`. Isolated filtering failure and same-probe HTTP recovery. | `PERMISSION_DEFERRED`. Approved lab network scope absent. |
| IR-03 | `DESIGNED`. UDR and next-hop contract. | `PERMISSION_DEFERRED`. Approved existing route-table scope absent. |
| IR-04 | `DESIGNED`. Peering connectivity contract. | `BUDGET_DEFERRED`. Peering, probes and traffic cost gate open. |
| IR-05 | `LOCAL_VERIFIED`. Kernel permission denial, minimal grant and negative controls. | `PERMISSION_DEFERRED`. Narrow Azure identity and data scope required. |
| IR-06 | `DESIGNED`. Key Vault access contract. | `BUDGET_DEFERRED`. Vault, transactions and network costs not established. |
| IR-07 | `LOCAL_VERIFIED`. Actual kubelet pull failure against a local HTTP 404 registry fixture, then readiness and HTTP 200. | `BUDGET_DEFERRED`. AKS/ACR compute, registry and network cost gate open. |
| IR-08 | `LOCAL_VERIFIED`. Real local state lock refusal, drift repair and a no-change plan. | `BUDGET_DEFERRED`. Storage transactions and retained state cost gate open. |
| IR-09 | `DESIGNED`. Azure Policy deny contract. | `PERMISSION_DEFERRED`. Dedicated policy scope and authorization required. |
| IR-10 | `LOCAL_VERIFIED`. Missed alert, rule correction and observed resolution. | `BUDGET_DEFERRED`. Telemetry, alert evaluation and retention cost gate open. |
| IR-11 | `LOCAL_VERIFIED`. Actual 500 and atomic same-probe restoration to HTTP 200. | `BLOCKED` at effective Linux verification after F1 provisioning. `CLEANED_UP`. Web App and release path `NOT_RUN`. |
| IR-12 | `LOCAL_VERIFIED`. Separate-path restore passed original SHA-256 and business value checks. | `BUDGET_DEFERRED`. Storage, retention and restore cost gate open. |

Both local cycles reported 8/8 mandatory scenarios verified and cleaned up. [Live-lab index](LIVE_LAB_INDEX.md) and [verification matrix](VERIFICATION_MATRIX.md).

## FinOps and closeout

Conditional gross project estimate is **USD 0.00** under the published F1 terms. Two historical Cost Management queries were throttled. The final pre- and post-run group-scoped month-to-date queries returned HTTP 200 with zero rows and no continuation. They returned no actual cost amount. Current billing is `BILLING_PENDING`. No unexpected charge was observed in the available data. The nominal balance is USD 1.00, with a USD 0.70 planning threshold and USD 0.30 contingency. Amount and effective headroom await delayed billing reconciliation. [Cost ledger](COST_LEDGER.md).

V1 is closed within the authorized scope. The unverified app exercise, deferred incidents, unexecuted KQL demo and pending billing remain on their own evidence lines.
