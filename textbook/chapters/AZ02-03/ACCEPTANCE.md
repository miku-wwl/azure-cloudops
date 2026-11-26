# AZ02-03 lecture acceptance record

**Lecture:** Azure Private DNS, Private Link and Private Endpoint

**Acceptance date:** 2026-11-26 (Pacific/Auckland)

**Status:** ACCEPTED for the Stage 1 lecture gate. No Azure access or resource operation was performed.

## Research and source mapping

- Microsoft Learn Private Endpoint, DNS integration, Azure Storage, VNet link and network policy pages were checked on 2026-11-26. Source-page revision dates and claim mapping are in `textbook/SOURCE_MAP.md`.
- Current CLI references were checked for Private Endpoint, DNS VNet links, A records and `NxDomainRedirect`. Pricing pages list endpoint-hour/data-processing, private DNS zone/query and resolver endpoint/ruleset charges; a precise live estimate is deferred because no authorized region, account offer, duration or resource scope is selected.
- The chapter distinguishes documented behavior from a clearly labeled inference about continuing the original service hostname for TLS/SNI. No TLS certificate or handshake was observed.
- Three original, editable figures are authored in `figures/figs.py`; their SVGs cover split-horizon DNS, hybrid resolver paths, and independent network/TLS/authorization gates.

## Experiment and evidence boundary

- `labs/private-dns-model` runs a narrow synthetic decision model over DNS visibility, a private A record, `NxDomainRedirect` fallback, endpoint status, public network access and a separate data-authorization assertion.
- 18 targeted unit tests passed on Windows Python 3.13.9. The complete Windows suite passed 63 tests across 5 directories; `devops-lab` WSL also passed 63 tests across 5 directories using `textbook/tools/test_all.sh --python`.
- The scenario script produced eight deterministic fixture results, including private success, public-path denial, NXDOMAIN, fallback, Pending approval and data authorization denial. Addresses use documentation-only fixtures.
- The model does not implement Azure DNS packets, CNAME recursion, caches/TTLs, Private Resolver, zone links/groups, routes, NSGs, TLS, Storage APIs or authorization evaluation. See the source README and chapter fidelity box.
- No Azure CLI login, subscription or billing query, Azure DNS resolution, resource read/write, TCP probe or Storage request was performed. The live lab remains `LIVE_NOT_RUN` pending Stage 3 gates.

## Publication inspection

- Reproduction: `python textbook/tools/build.py AZ02-03`.
- Output: `textbook/dist/pdf/AZ02-03_azure-private-dns-link-endpoint.pdf`; 11 pages, 1,788,591 bytes, SHA-256 `043E08939C171E92BB6AB090642A50A8F991FC227D46CA59A5460ABC86179B18`.
- Final build report: 20,822 extracted characters, no placeholder markers, no overflow warnings, page fill 65%, 99%, 79%, 82%, 97%, 84%, 98%, 74%, 87%, 96%, 77%.
- All 11 final PDF pages were rendered and reviewed in six readable two-page spreads on 2026-11-26. Review covered typography, diagrams, CNAME/private-zone table, examples, code, lab output, fault cards, exercises/solutions, evidence record, references, page numbers and margins.
- Publisher QA continues to emit the existing non-blocking Pillow `Image.getdata()` deprecation warning.

## Gate result

**PASS — current primary-source mapping, Chinese chapter, three editable figures, local model, Windows/WSL tests, future read-only lab preparation, PDF build and all-page visual review are complete.** No Azure behavior, endpoint connectivity, data access, billing or live cost has been claimed.
