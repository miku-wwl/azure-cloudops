# FIN-01 acceptance — Azure FinOps and resource cost recovery

- Acceptance date: 2026-11-27 (Pacific/Auckland).
- Gate: ACCEPTED for the offline lecture milestone only; Stage 1 B9 remains separate.
- Deliverable: `textbook/dist/pdf/FIN-01_azure-finops-resource-cost-recovery.pdf`.
- PDF: 9 pages, 1,745,465 bytes; SHA-256 `B84F35E95AD74B3419618BE5F93990CB98064C93E4A6222459E8F1657A9E06DC`.

## Scope and learning result

The chapter teaches meter-based estimation, cost-data freshness, actual versus amortized views, budget alerts, tags and inherited cost attribution, shared-cost allocation, Reservations versus Savings Plans, VM billing states, retained dependencies, and a verified resource-cost recovery loop. It includes a fictional worked ledger, an owner/retention fault card, exercises with solution points, and a future read-only runbook.

The claim map and research date are recorded in [`textbook/SOURCE_MAP.md`](../../SOURCE_MAP.md). Official sources include the Azure Pricing Calculator, Retail Prices API, Cost Management budgets/query/data freshness/tag inheritance/allocation, Reservation and Savings Plan guidance, VM billing states, attached-resource deletion behavior, and Azure Advisor cost recommendations. Five original mechanism figures are generated from editable Python in `figures/figs.py`.

## Local verification

- `python textbook/tools/build.py FIN-01` generated nine pages and 10,868 extracted characters. The build report found no placeholder markers. Page fill was 20%, 99%, 66%, 83%, 95%, 86%, 89%, 93% and 59%, including the intentionally sparse cover.
- Every page was rendered and visually reviewed in page pairs at 88 DPI and 140 DPI. The first review caught duplicate section numbering and an incomplete source-output excerpt; these were corrected before the final rebuild. Final title hierarchy, figures, table, code output, references, margins, page breaks and numbering were checked without clipping or corruption.
- The synthetic ledger baseline reports USD 180.50 gross charges, USD 12.00 credits, USD 168.50 net, USD 171.00 allocated gross and USD 9.50 unallocated gross. These values are fictional lab data, not an Azure estimate or bill.
- FIN-01's local suite passed 27 tests. The full Python suite passed on Windows and in the `devops-lab` WSL distribution: 402 tests across 22 test directories, zero failing directories.
- The teaching model separates gross charges, credits and net; selects one view at a time; checks allocation reconciliation and tag inheritance; reports budget thresholds as `alert_only`; calculates hourly unused commitment; and returns review decisions without resource changes. It is not a Cost Management export parser, Azure pricing engine, reservation matcher, or deletion tool.

## Authorization, live scope and cost boundary

[`FUTURE-LIVE-READONLY.md`](labs/cost-recovery/FUTURE-LIVE-READONLY.md) is documentation only and is marked `NOT_RUN`. It requires Stage 3 L0 scope and separate authorization before any Azure login/query session. No Azure authentication, account enumeration, Cost Management query, Advisor request, resource inventory request, resource change, export creation, or billing query occurred for this acceptance. No Azure resource was created or changed.

No actual Azure cost is estimated or claimed. The future read-only query has no reviewed live cost estimate. Actual cumulative Azure spend remains `NOT_VERIFIED`; no USD 0.00 actual-spend claim is made. The project-wide cumulative ceiling remains USD 1.00 with a USD 0.70 planning threshold.

## Release decision

The research-backed chapter, editable figures, local synthetic lab, documented read-only procedure, PDF and visual checks meet the FIN-01 offline lecture gate. Stage 1's B9 package acceptance and all Stage 2 engineering gates remain separate.
