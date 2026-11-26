# Project progress

- Last updated: 2026-11-26 (Pacific/Auckland)
- Repository: D:/workshop/nov/azure-cloudops
- Branch: main
- Starting and approved V3 baseline: 853ba6cbaa4ee67e448550fbe192c6c89b24fd2f

## Current gate

- Overall stage: Stage 1 — Technical Textbook Engineering & Publication
- Current phase: B2 — Lectures 03–06; B1 passed its two lecture acceptance gates.
- B0 status: COMPLETE. Read-only AWS source, toolchain, two reference PDFs and package consistency reviewed; Azure publisher adaptation built an Azure chapter and passed the recorded checks.
- Completed lectures: 4/23 — AZ00-01, AZ01-01, AZ02-01 and AZ02-02. AZ02-03 is next.
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
- The offline Python runner now discovers 4 lab directories and passes all 45 unit tests in `devops-lab` WSL.
- AZ02-01 passed its lecture gate: current Microsoft routing/Network Watcher research, three editable diagrams, a narrow synthetic route-selection/asymmetric-path model, 13 Windows tests and a full WSL run of 32 tests across 3 directories. Its 8-page PDF was rendered and all pages visually reviewed; see `chapters/AZ02-01/ACCEPTANCE.md`. No Azure request or route operation was performed.
- AZ02-02 passed its lecture gate: current NSG/ASG/Network Watcher research, three editable figures, a synthetic custom-rule/stateful-flow model, 13 Windows tests and a full WSL run of 45 tests across 4 directories. Its 8-page PDF was rendered and all pages visually reviewed; see `chapters/AZ02-02/ACCEPTANCE.md`. No Azure security rule or connectivity operation was performed.
- Azure publisher QA still emits the non-blocking Pillow `Image.getdata()` deprecation warning.

## First next action

Research AZ02-03 with current Microsoft Private DNS, Private Link and private endpoint documentation; author a DNS-chain and endpoint-name-resolution experiment, then run the full lecture acceptance sequence before AZ02-04.
