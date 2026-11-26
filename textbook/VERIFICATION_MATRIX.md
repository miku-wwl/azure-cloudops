# Verification matrix

Verification states are independent. A documented or local result does not establish Azure behavior.

| Evidence class | Meaning |
|---|---|
| PLANNED | Scope accepted; implementation or execution has not started |
| DOCUMENTED | Requirements and procedure written; not executed |
| DESIGNED | Architecture or mechanism reasoned through; not executed |
| STATIC_CHECK_PASS | A stated static check actually passed |
| LOCAL_VERIFIED | A stated mechanism executed locally under recorded conditions |
| DEMO_VERIFIED | An official demonstration environment was actually queried |
| READ_ONLY_AZURE_VERIFIED | An authorized Azure read-only query actually completed |
| PLAN_VERIFIED | An exact cloud plan was reviewed; resources were not applied |
| DEPLOYED | Cloud resource creation was observed |
| LIVE_VERIFIED | The intended Azure mechanism and functional assertions passed |
| RECOVERED | A controlled failure was repaired and the same probe passed |
| CLEANED_UP | Approved temporary resources were deleted and residuals inspected |
| LIVE_NOT_RUN | No live execution occurred |
| BILLING_PENDING | Billing evidence is delayed or unavailable |
| BUDGET_DEFERRED | Reliable cost estimate exceeds the project planning threshold |
| PERMISSION_DEFERRED | Required narrow authorization is unavailable |
| BLOCKED / FAIL / PARTIAL | Actual blocker, failed check or incomplete acceptance |

## Starting state (approved baseline 853ba6c)

| Area | Status | Evidence |
|---|---|---|
| Azure repository | CLEAN at approved baseline at task start | git status and origin/main after fetch |
| AWS reference package consistency | STATIC_CHECK_PASS (reference only) | AWS package.py --verify; 19 PDFs and 445 source-package files |
| AWS sample PDF visual review | Reviewed representative scope only | A00-01 22 pages and FIN-01 10 pages as described in REFERENCE_ANALYSIS.md |
| Azure curriculum | DOCUMENTED | CURRICULUM.md |
| Azure chapter PDFs and experiments | PLANNED | No Azure chapters have passed acceptance yet |
| Azure resource creation | LIVE_NOT_RUN | No mutation performed |
| Azure billing | NOT_VERIFIED | No billing query performed |

Every lecture and incident will receive its own evidence and limitations before a release milestone is considered.

## Current Stage 1 evidence (2026-11-26)

| Lecture | Evidence | Limit |
|---|---|---|
| AZ00-01 | ACCEPTED; 8-page PDF, 3 figures, 7 local tests | No Azure authentication, RBAC query or Provider registration |
| AZ01-01 | ACCEPTED; 7-page PDF, 3 figures, 12 local tests | Synthetic topology only; no Azure availability, SLA or recovery drill |
| AZ02-01 | ACCEPTED; 8-page PDF, 3 figures, 13 local tests; WSL suite 32 tests across 3 directories | Synthetic narrow IPv4 model; no Azure route, NVA or connectivity query |
| AZ02-02 | ACCEPTED; 8-page PDF, 3 figures, 13 local tests; WSL suite 45 tests across 4 directories | Synthetic custom NSG model; no Azure effective-rule or probe query |
| AZ02-03 | ACCEPTED; 11-page PDF, 3 figures, 18 local tests; full Windows and WSL suites each passed 63 tests across 5 directories | Synthetic DNS/access model; no Azure DNS, PE, TLS, Storage or billing query |
| AZ02-04 | ACCEPTED; 9-page PDF, 3 figures, 20 local tests; Windows + WSL suites each passed 83 tests across 6 directories | Synthetic probe contracts and priority candidates only; no Azure health, routing, WAF, TLS, network or billing observation |
| AZ03-01 | ACCEPTED; 9-page PDF, 3 figures, 17 local tests; Windows + WSL suites each passed 100 tests across 7 lab directories | Synthetic token assertions and RBAC fixture only; no JWT, Entra/Azure/Graph query, role change or billing observation |
| AZ03-02 onward | PLANNED | Not yet authored or run |

All seven accepted lecture PDFs are independent outputs in textbook/dist/pdf/. Package verification awaits all 23 chapters.
