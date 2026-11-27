# AZ02-01 lecture acceptance record

**Lecture:** Azure VNet, UDR and Effective Routes

**Acceptance date:** 2026-11-26 (Pacific/Auckland)
**Status:** ACCEPTED for Stage 1 lecture gate. Azure routing and connectivity were not queried or exercised.

## Research and source

- Microsoft Learn and Azure CLI primary sources were reviewed on 2026-11-26. Claim mappings, direct URLs, classifications and limitations are recorded in `textbook/SOURCE_MAP.md`.
- The lecture distinguishes subnet route-table association, VM NIC effective routes, longest-prefix match, equal-prefix UDR/BGP/system priority and documented system-route exceptions.
- The asymmetric-flow example is grounded in the documented Azure Virtual WAN dual-role active-active NVA case; it does not claim universal behavior for all Azure paths.
- Three original editable mechanism figures are authored in `figures/figs.py`; they illustrate route selection, asymmetric stateful inspection and diagnostic evidence boundaries.

## Experiment and evidence boundary

- `labs/route-model` loads fictional IPv4 system, BGP and UDR fixtures, tests longest-prefix and equal-prefix selection, verifies association boundaries, handles a `None` blackhole and compares two explicitly modeled directions through a stateful appliance.
- The model refuses special system-route semantics and ambiguous equal-best routes rather than inventing a result. It is not an Azure emulator and does not model BGP convergence, NIC effective-route retrieval, ECMP, a real gateway/NVA, NSGs, DNS, transport connectivity or service behavior.
- Stage 1 baseline: thirteen unit tests passed on Windows Python 3.13.9 on 2026-11-26. The full WSL `test_all.sh --python` run passed 32 tests across 3 lab directories with 0 failures. See the E0 addendum below for the corrected current test count.
- No Azure CLI authentication, subscription query, Next Hop request, route change, resource deployment, connection test or Azure billing query was performed.

## Publication inspection

- Reproduction from the repository root: `python textbook/tools/build.py AZ02-01`.
- Stage 1 output: `textbook/dist/pdf/AZ02-01_azure-vnet-udr-effective-routes.pdf`; 8 pages, 1,704,724 bytes. See the E0 addendum for the corrected artifact hash and size.
- Final automated report: 11,748 extracted characters; no placeholder markers; no overflow warnings; page fill 53%, 99%, 96%, 96%, 99%, 78%, 87%, 55%.
- All eight final pages were rendered and visually inspected in readable two-page spreads on 2026-11-26. The cover, route-selection table/figure, caveat boxes, asymmetric-path figure, CLI blocks, lab output, fault cards, exercises/solutions, references, headers, page numbers and margins were checked.
- The build completes with the existing non-blocking Pillow `Image.getdata()` deprecation warning in the QA ink calculation.

## Gate result

**PASS — current primary-source mapping, chapter source, editable diagrams, applicable local experiment, actual tests, read-only live-lab instructions, PDF build, all-page visual review and evidence record are complete.** The result does not claim Azure route selection, NVA behavior or connectivity was verified.

## E0 independent-audit addendum (2026-11-27)

- Audit defect: `Route.from_dict` accepted arbitrary nonempty `next_hop_type` strings. A typo could pass through fixture evaluation as if it were a valid route. It also allowed an unused `next_hop_ip` on non-appliance routes and required the fixture author to tag special next-hop types manually.
- Correction: validate next-hop values against the official route vocabulary, accept `next_hop_ip` only for `VirtualAppliance`, and infer/refuse recognized special next-hop cases. Primary source: [Azure Routes REST schema](https://learn.microsoft.com/en-us/rest/api/virtualnetwork/routes/get?view=rest-virtualnetwork-2026-01-01) and [Azure virtual network routing](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview).
- Three regression tests were added. All 16 route-model tests passed on Windows Python 3.13.9. The chapter and lab instructions now reflect the stricter fixture contract. The Azure control plane was not queried.
- The updated eight-page PDF was rebuilt (11,983 extracted characters; no placeholder markers), rendered as four page-pair sheets, and every page was visually checked. Current artifact: 1,723,150 bytes; SHA-256 `0A783F06FF14484D635076874A9927CBC008E18D09FDD9A14188125E4A92B77A`.
- The full Windows and WSL suites each pass 407 tests across 22 directories. No Azure request was made.
