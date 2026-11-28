# FIN-01 acceptance — Azure FinOps and resource cost recovery

## V1.0.1 教材修订

- 补预算与磁盘对账操作，区别承诺利用率和超出承诺的用量。
- 最终教材 [PDF](../../dist/pdf/FIN-01_azure-finops-resource-cost-recovery.pdf) 已用原出版工具重建。基线 9 页，修订 9 页。正文排入 5 个 SVG，保留 5 个可编辑图稿。最终页面已检查排版、图和代码，带入全套发布校验。
- 现有本地回归通过。新增云端步骤按文档例处理，历史证据与操作权限见 [V1.0.1 逐讲审查](../../V1_0_1_TEXTBOOK_REVIEW.md)。

- Acceptance date: 2026-11-27 (Pacific/Auckland).
- Gate: ACCEPTED for the offline lecture milestone; Stage 1 B9 publication acceptance was recorded separately.
- Deliverable: `textbook/dist/pdf/FIN-01_azure-finops-resource-cost-recovery.pdf`.
- Stage 1 PDF: 9 pages, 1,745,465 bytes; SHA-256 `B84F35E95AD74B3419618BE5F93990CB98064C93E4A6222459E8F1657A9E06DC`. See the E0 addendum for the corrected artifact hash and size.

## Scope and learning result

The chapter teaches meter-based estimation, cost-data freshness, actual versus amortized views, budget alerts, tags and inherited cost attribution, shared-cost allocation, Reservations versus Savings Plans, VM billing states, retained dependencies, and a verified resource-cost recovery loop. It includes a fictional worked ledger, an owner/retention fault card, exercises with solution points, and a future read-only runbook.

The claim map and research date are recorded in [`textbook/SOURCE_MAP.md`](../../SOURCE_MAP.md). Official sources include the Azure Pricing Calculator, Retail Prices API, Cost Management budgets/query/data freshness/tag inheritance/allocation, Reservation and Savings Plan guidance, VM billing states, attached-resource deletion behavior, and Azure Advisor cost recommendations. Five original mechanism figures are generated from editable Python in `figures/figs.py`.

## Local verification

- `python textbook/tools/build.py FIN-01` generated nine pages and 10,868 extracted characters. The build report found no placeholder markers. Page fill was 20%, 99%, 66%, 83%, 95%, 86%, 89%, 93% and 59%, including the intentionally sparse cover.
- Every page was rendered and visually reviewed in page pairs at 88 DPI and 140 DPI. The first review caught duplicate section numbering and an incomplete source-output excerpt; these were corrected before the final rebuild. Final title hierarchy, figures, table, code output, references, margins, page breaks and numbering were checked without clipping or corruption.
- The synthetic ledger baseline reports USD 180.50 gross charges, USD 12.00 credits, USD 168.50 net, USD 171.00 allocated gross and USD 9.50 unallocated gross. These values are fictional lab data, not an Azure estimate or bill.
- Stage 1 baseline: FIN-01's local suite passed 27 tests. The full Python suite passed on Windows and in the `devops-lab` WSL distribution: 402 tests across 22 test directories, zero failing directories. See the E0 addendum for the corrected current test count.
- The teaching model separates gross charges, credits and net; selects one view at a time; checks allocation reconciliation and tag inheritance; reports budget thresholds as `alert_only`; calculates hourly unused commitment; and returns review decisions without resource changes. It is not a Cost Management export parser, Azure pricing engine, reservation matcher, or deletion tool.

## Authorization, live scope and cost boundary

[`FUTURE-LIVE-READONLY.md`](labs/cost-recovery/FUTURE-LIVE-READONLY.md) is documentation only and is marked `NOT_RUN`. It requires Stage 3 L0 scope and separate authorization before any Azure login/query session. No Azure authentication, account enumeration, Cost Management query, Advisor request, resource inventory request, resource change, export creation, or billing query occurred for this acceptance. No Azure resource was created or changed.

No actual Azure cost is estimated or claimed. The future read-only query has no reviewed live cost estimate. Actual cumulative Azure spend remains `NOT_VERIFIED`; no USD 0.00 actual-spend claim is made. The project-wide cumulative ceiling remains USD 1.00 with a USD 0.70 planning threshold.

## Release decision

The research-backed chapter, editable figures, local synthetic lab, documented read-only procedure, PDF and visual checks meet the FIN-01 offline lecture gate. Stage 1's B9 package acceptance and all Stage 2 engineering gates remain separate.

## E0 independent-audit addendum (2026-11-27)

- Audit defect: shared allocations rounded every cost-center share independently to cents. A one-cent 50/50 pool rounded to zero total and failed the reconciliation gate; other fractions could create or lose cents.
- Correction: use deterministic largest-remainder allocation in integer cents, with stable cost-center ordering for equal remainders. Add regression coverage for one-cent and two-cent pools; the suite now has 29 tests, all passing on Windows Python 3.13.9.
- The historical Stage 1 PDF values remain unchanged because the fixture weights divide evenly. The chapter and lab text now state the cents-preserving rule. The updated nine-page PDF was rebuilt (10,913 extracted characters; no placeholder markers), rendered as five page-pair sheets, and every page was visually checked. Current artifact: 1,749,094 bytes; SHA-256 `C706F37752378D0D4A80463532CF76A8301D6BF75DB0A0BAC6E1F2E94AE3A880`.
- The full Windows and WSL suites each pass 407 tests across 22 directories. No Azure pricing or billing query was made. Updated source and PDF ZIP consistency remain part of Stage 2 publication acceptance.

## V1 closure addendum (2026-11-28)

- Distinguished the conditional USD 0.00 gross estimate, two successful empty scoped query responses and pending billing. Improved figure 23-2 amount labels and confirmed the regenerated visual.
- [Final PDF](../../dist/pdf/FIN-01_azure-finops-resource-cost-recovery.pdf) has 9 pages and 1,782,366 bytes. SHA-256 is `1238664BF40E43798AE9F67E8BF0DA17EA19C8F6A29E58CC7150D32ECCF57D01`.
- Visually inspected all 9 pages at 88 DPI and page 4 at 140 DPI. The final page proof was compared with the prior reviewed render and every changed page was rechecked. Publisher QA, PDF outline and extracted text checks passed.
- Scope and observed evidence are linked from the [V1 source map](../../SOURCE_MAP.md#v1-closure-source-map--2026-11-28).
