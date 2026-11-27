# Azure CloudOps — final acceptance and handoff

- As of: 2026-11-27 (Pacific/Auckland)
- Repository: D:/workshop/nov/azure-cloudops
- Branch: main
- Status: Stages 1 and 2 accepted; Stage 3 L0 read-only preflight complete; live Azure incident execution awaits one exact owner approval.

## Acceptance summary

The repository contains all 23 approved Chinese technical textbooks, editable sources, 95 original SVG mechanism figures, offline experiments, Terraform and Azure Pipelines examples, 12 incident contracts, eight mandatory local incident scenarios with evidence, reproducible publishing tools and verified PDF/source ZIP packages. The work did not change Azure resources.

Stage 1 B0–B9 and Stage 2 E0–E10 passed their documented gates. Every final textbook PDF was rendered and visually reviewed as recorded in its chapter acceptance evidence. The final Stage 2 source refresh did not alter PDF payloads. There are zero genuine Azure Portal screenshots; no portal image was fabricated.

Stage 3 L0 completed using the existing Azure CLI session. All Azure incident mutations remain NOT_RUN. The Cost Management Usage query was throttled twice, so actual subscription billing remains NOT_VERIFIED. See L0_READ_ONLY_PREFLIGHT.md.

## Publication set

The PDFs contain 183 pages in total. [Azure-CloudOps-PDF.zip](dist/Azure-CloudOps-PDF.zip) has SHA-256 `575F22B9958B68752B54539534E020902135B04BFF22C0BAF0924C8AA0C65608` (28,080,948 bytes). The verified [Azure-CloudOps-Sources.zip](dist/Azure-CloudOps-Sources.zip) contains 427 source and evidence files; the package verifier confirmed its contents match the current source tree. Its hash is intentionally not embedded in the archive contents because that would make the archive hash self-referential.

| Lecture | Pages | Lecture | Pages | Lecture | Pages |
|---|---:|---|---:|---|---:|
| AZ00-01 | 8 | AZ01-01 | 7 | AZ02-01 | 8 |
| AZ02-02 | 8 | AZ02-03 | 11 | AZ02-04 | 9 |
| AZ03-01 | 9 | AZ03-02 | 9 | AZ03-03 | 8 |
| AZ04-01 | 6 | AZ04-02 | 7 | AZ04-03 | 9 |
| AZ04-04 | 8 | AZ05-01 | 6 | AZ05-02 | 7 |
| AZ05-03 | 7 | AZ06-01 | 7 | AZ06-02 | 7 |
| AZ07-01 | 9 | AZ07-02 | 7 | AZ07-03 | 8 |
| AZ08-01 | 9 | FIN-01 | 9 | Total | 183 |

## Engineering and test evidence

- E8 executed all eight mandatory incidents locally using bounded mechanisms; each recorded a fault, diagnosis, same-probe recovery and cleanup. The LAB-IR-11 candidate packages were also built and locally verified: the same GET /health probe observed known-good 200, intentional 500 and restored 200 responses. E10 replayed all eight in a second clean cycle and replayed network, identity/permission and data-recovery cases in distinct contexts. This is local execution replay, not Azure validation or independent human review.
- Final local Stage 2 gates: Python 3.13.9 passed 515 tests across 24 directories in the refreshed Windows run; Terraform 1.15.5 passed recursive formatting, backend-free init/validate and 13 plan/mock test runs across three roots; Pester 5.7.1 passed 2/2 tests.
- Repository verification covers 23 curriculum/source/PDF mappings, 154 local Markdown references and 13 E9 cards with 18 required fields each. The IR-11 package test asserts root ZIP layout, response status and release body. The package verifier confirms all 23 PDF payloads and source archive contents match the source tree.
- GitHub Actions run [45960683857](https://github.com/miku-wwl/azure-cloudops/actions/runs/45960683857) passed all five jobs at code revision 82d7865cc0b4df9ea4ea4eae595a2eaca726441d: Windows and Ubuntu repository/Python checks, Terraform format/validate/mock checks, Pester tooling checks, package/reference verification and a full-history Gitleaks scan. This report, the IR-11 package test and source archive are included in the published revision; its exact-revision result is tracked by the [GitHub Actions workflow](https://github.com/miku-wwl/azure-cloudops/actions/workflows/ci.yml) and linked in the delivery handoff.
- The workflow uses pinned actions and test dependencies, read-only permissions and no artifacts or comments containing Azure data. Hosted GitHub usage is outside the Azure budget.

## Latest Stage 3 safety-gate refresh (2026-11-27)

The LAB-IR-11 runbook now requires the exact approved batch, tenant/subscription, rechecked price/offer and service-limit attestations, and a gross estimate of USD 0.00. It checks the documented regional Free-plan count from the subscription inventory, starts an independent cleanup watchdog before the first write, and keeps that watchdog monitoring after the primary cleanup marker through a bounded final verification window. The watchdog deletes only the exact project/run-tagged dedicated resource group. The official Microsoft.Web usage endpoint was confirmed to report core usage, not an F1 plan count; the prior 0/2 interpretation was withdrawn and F1 count, entitlement, capacity and actual billing remain NOT_VERIFIED.

The latest local source refresh passed 528 Python tests across 24 directories, the repository verifier (23 mappings, 155 Markdown references and 13 complete catalogue cards), Terraform formatting/backend-free validation and 13 plan/mock tests across three roots, the PowerShell parser and byte-for-byte package verification. The refreshed source ZIP contains 427 files; the 23-PDF ZIP and its SHA-256 are unchanged. No Azure request or mutation occurred during this refresh. The exact published revision's hosted Pester and Gitleaks checks are tracked by its GitHub Actions run.

## Incident state

The eight mandatory local incidents are IR-01, IR-02, IR-05, IR-07, IR-08, IR-10, IR-11 and IR-12. Their real local mechanisms and results are documented in E8_LOCAL_INCIDENTS.md, incidents/evidence/ and E10_INDEPENDENT_REPLAY.md. Four other contracts remain design-only by the approved plan. Every Azure live status IR-01 through IR-12 is NOT_RUN. Local outcomes do not substitute for Azure behavior.

## Azure L0 evidence and limits

The L0 results and subsequent evidence correction are recorded in L0_READ_ONLY_PREFLIGHT.md. In summary, the current CLI session remained enabled and default; two subscription-scope Owner assignment records were returned for the current principal, without an evaluation of group-derived permissions; one resource group and three Network Watcher resources were listable; Microsoft.Web and Microsoft.Insights were registered; Australia East was supported and the Linux F1 location was available. An earlier 0/2 response was misinterpreted as an F1 instance quota. Microsoft's regional usage API documents core usage, so F1 plan count, entitlement and regional capacity remain NOT_VERIFIED. No project lab VNet, NSG, route table, NIC or App Service appeared in the listable inventory. A proposed resource group was absent and a candidate app name was available at the time checked.

No resource, provider registration, diagnostic probe, app deployment or other Azure mutation was performed. Two Cost Management Usage queries returned HTTP 429, with no amount obtained. Actual cumulative Azure billing is NOT_VERIFIED; no USD 0.00 actual-spend claim is made.

## Proposed Stage 3 batch — approval required

The only current candidate is LAB-IR-11, an isolated App Service release-regression and rollback drill. This is a proposal, not authorization.

- Exact resource allowlist: create resource group rg-azure-cloudops-ir11-aue; within it create one Linux App Service plan asp-azure-cloudops-ir11-aue with SKU F1 and one web app azcoir11aue261126. Region: Australia East (australiaeast). The group was absent and site name was available when checked; repeat both checks immediately before any write.
- Operation: deploy the no-dependency Node 24 LTS ZIP packages sequentially to the same app and HTTPS endpoint: known-good response, deterministic HTTP 500 fault, then the exact same known-good ZIP. Use the reviewable NODE:24-lts source in incidents/live_ir11 and capture baseline, fault and recovery status/body with the same GET /health probe. Do not create deployment slots, production routes, Application Insights, Log Analytics, Storage, private networking or extra resources.
- Maximum lifetime: 45 minutes from creation through recovery, teardown and residual-resource check. Delete the app, plan and dedicated resource group in the same run; verify no residual resources.
- Price basis: Microsoft lists Linux App Service F1 as USD 0 with shared CPU limited to 60 CPU minutes/day, 1 GB RAM and 1 GB storage; Azure bandwidth pricing lists the first 100 GB/month of internet egress as free. Sources: [App Service Linux pricing](https://azure.microsoft.com/en-us/pricing/details/app-service/linux/), [Azure bandwidth pricing](https://azure.microsoft.com/en-au/pricing/details/bandwidth/), and [App Service hosting plans](https://learn.microsoft.com/en-us/azure/app-service/overview-hosting-plans).
- Estimate: conditional USD 0.00 gross for the proposed 45-minute run under the published terms, if the account offer includes F1 and no paid dependencies are needed. F1 plan count, entitlement and regional capacity were not established at L0; the runtime list included NODE:24-lts. Recheck the documented regional Free-plan limit, account offer and current pricing immediately before creation. Stop if F1 is unavailable, a paid dependency is needed, an unexpected meter appears, or the reliable cumulative gross estimate exceeds USD 0.70. Keep USD 0.30 as contingency and never exceed the project USD 1.00 ceiling.
- Authorization needed: explicit approval of this exact resource group, plan, app, region/SKU, operation, 45-minute limit, teardown and conditional cost gate. Approval would not authorize other Azure resource changes.

The source, package builder, same probe, local package/watchdog tests and guarded Azure CLI sequence are reviewable in incidents/live_ir11/README.md. The full catalogue card is LAB-IR-11 in LIVE_LAB_CATALOGUE.md. The project proceeds to Azure writes only after this batch is specifically approved and every run-time gate passes. If the owner declines or cost/offer/plan-limit evidence cannot be confirmed, keep all Azure live incident states NOT_RUN.
