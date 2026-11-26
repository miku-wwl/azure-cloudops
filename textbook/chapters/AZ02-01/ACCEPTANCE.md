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
- Thirteen unit tests passed on Windows Python 3.13.9 on 2026-11-26. The full WSL `test_all.sh --python` run passed 32 tests across 3 lab directories with 0 failures.
- No Azure CLI authentication, subscription query, Next Hop request, route change, resource deployment, connection test or Azure billing query was performed.

## Publication inspection

- Reproduction from the repository root: `python textbook/tools/build.py AZ02-01`.
- Output: `textbook/dist/pdf/AZ02-01_azure-vnet-udr-effective-routes.pdf`; 8 pages, 1,704,724 bytes.
- Final automated report: 11,748 extracted characters; no placeholder markers; no overflow warnings; page fill 53%, 99%, 96%, 96%, 99%, 78%, 87%, 55%.
- All eight final pages were rendered and visually inspected in readable two-page spreads on 2026-11-26. The cover, route-selection table/figure, caveat boxes, asymmetric-path figure, CLI blocks, lab output, fault cards, exercises/solutions, references, headers, page numbers and margins were checked.
- The build completes with the existing non-blocking Pillow `Image.getdata()` deprecation warning in the QA ink calculation.

## Gate result

**PASS — current primary-source mapping, chapter source, editable diagrams, applicable local experiment, actual tests, read-only live-lab instructions, PDF build, all-page visual review and evidence record are complete.** The result does not claim Azure route selection, NVA behavior or connectivity was verified.
