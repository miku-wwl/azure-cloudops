# Project progress

- Last updated: 2026-11-26 (Pacific/Auckland)
- Repository: D:/workshop/nov/azure-cloudops
- Branch: main
- Starting and approved V3 baseline: 853ba6cbaa4ee67e448550fbe192c6c89b24fd2f

## Current gate

- Overall stage: Stage 1 — Technical Textbook Engineering & Publication
- Current phase: B2 — Lectures 03–06, 4/4 lectures accepted. Next phase B3 — AZ03-01 through AZ03-03; 0/3 accepted.
- B0 status: COMPLETE. Read-only AWS source, toolchain, two reference PDFs and package consistency reviewed; Azure publisher adaptation built an Azure chapter and passed the recorded checks.
- Completed lectures: 6/23 — AZ00-01, AZ01-01 and AZ02-01 through AZ02-04. AZ03-01 is next.
- Implementation is being tracked on main from the approved baseline; see repository history for the current checkpoint.
- Cloud resource operations: none performed for this project.
- Azure authorization and subscription scope: NOT_CHECKED; Stage 3 read-only preflight is later.
- Actual Azure billing: NOT_VERIFIED; billing source not queried. Do not report USD 0 actual spend.
- Known host limit: Podman is not installed. Container and local Kubernetes runtime capability remains unverified.

## Stage sequence

1. Stage 1: B0 reference/publisher; B1 lectures 01–02; B2 03–06; B3 07–09; B4 10–13; B5 14–16; B6 17–18; B7 19–21; B8 22–23; B9 full technical/editorial/publication acceptance.
2. Stage 2: E0 independent audit; E1 architecture contracts; E2 local lab substrate; E3 Terraform; E4 state and controlled delivery; E5 Azure DevOps; E6 diagnostics and automation; E7 twelve incidents; E8 eight mandatory local incidents; E9 live-lab preparation; E10 independent replay.
3. Stage 3: L0 read-only Azure preflight, followed only by specifically authorized, reliably costed live experiments within the cumulative USD 1.00 ceiling.

## Completed evidence

- Target main and origin/main were synchronized at the approved V3 commit; no owner changes were present at start.
- AWS reference checkout was exact commit b44160ea0f864ce7edf40cc0edb402cb53687a63 and clean. No AWS files were modified.
- AWS PDF and source ZIP verifier passed read-only. See REFERENCE_ANALYSIS.md for scope and limits.
- Representative AWS PDF pages were rendered and visually reviewed as recorded in REFERENCE_ANALYSIS.md.
- Adapted Azure publisher built AZ00-01 into an 8-page PDF. The final build reported 13,443 extracted characters, no placeholder markers, no overflow warnings, and page fill 49–100% (cover 49%). All eight pages were rendered and visually inspected; confirmed code wrapping and reference-label breaks were corrected and the affected pages rebuilt and rechecked. Automated render report: `textbook/chapters/AZ00-01/build/qa/report.txt` (ignored local artifact).
- AZ00-01 official-source map, three original mechanism figures, seven local unit tests, synthetic scope fixture and fidelity limits are recorded in `chapters/AZ00-01/ACCEPTANCE.md` and `SOURCE_MAP.md`. No Azure CLI query, authentication, provider registration or resource mutation was run.
- `test_all.sh --python` passed the AZ00-01 suite in the `devops-lab` WSL distribution: 7 tests, 1 test directory, 0 failures. Windows Python 3.13.9 test output in the lecture is a separate local run.
- Initial publisher checks: Python compilation, Node syntax, and `test_all.sh` shell syntax passed; no Terraform chapter exists yet, and the package gate awaits all 23 PDFs.
- The adapted publisher prints a non-blocking Pillow `Image.getdata()` deprecation warning; build succeeds. Podman is unavailable on this host.
- AZ01-01 passed its lecture gate with current Microsoft Learn research, three original figures, a deterministic reliability/failure-matrix lab and 12 unit tests. Its 7-page PDF was rendered and all pages visually inspected after correcting markup, pagination, diagram scope and reference wrapping. See `chapters/AZ01-01/ACCEPTANCE.md`.
- At the AZ02-02 checkpoint, the offline Python runner discovered 4 lab directories and passed 45 tests in `devops-lab` WSL.
- AZ02-01 passed its lecture gate: current Microsoft routing/Network Watcher research, three editable diagrams, a narrow synthetic route-selection/asymmetric-path model, 13 Windows tests and a full WSL run of 32 tests across 3 directories. Its 8-page PDF was rendered and all pages visually reviewed; see `chapters/AZ02-01/ACCEPTANCE.md`. No Azure request or route operation was performed.
- AZ02-02 passed its lecture gate: current NSG/ASG/Network Watcher research, three editable figures, a synthetic custom-rule/stateful-flow model, 13 Windows tests and a full WSL run of 45 tests across 4 directories. Its 8-page PDF was rendered and all pages visually reviewed; see `chapters/AZ02-02/ACCEPTANCE.md`. No Azure security rule or connectivity operation was performed.
- Azure publisher QA still emits the non-blocking Pillow `Image.getdata()` deprecation warning.

- AZ02-03 passed its lecture gate: Microsoft Private Link/Storage/Private DNS research, three editable figures, an 18-test synthetic DNS/access decision model, full Windows and WSL runs of 63 tests across 5 lab directories, and an 11-page PDF with all pages visually inspected. Its source map and evidence record distinguish documented behavior, TLS inference and model limits. No Azure authentication, DNS query, resource operation, network probe or billing query was performed.
- AZ02-04 passed its lecture gate: current Microsoft Load Balancer, Application Gateway and Front Door research, three editable mechanism figures, a 20-test synthetic probe/priority decision model, Windows and WSL full-suite runs of 83 tests across 6 lab directories, and a 9-page A4 PDF with all pages reviewed (pages 3–4 also at 140 DPI). The source map distinguishes service documentation from local results and model limits. No Azure authentication, query, probe, WAF request, resource operation or billing query was performed.

## First next action

Research AZ03-01 with current Microsoft Entra ID token and Azure RBAC documentation; design a narrow offline model that separates identity, token audience, action/DataAction and scope inheritance, then run its full lecture acceptance sequence. Do not query Entra ID, Azure RBAC or a subscription before Stage 3 gates.
