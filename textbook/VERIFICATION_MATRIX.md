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

## Current Stage 1 evidence (2026-11-27)

| Lecture | Evidence | Limit |
|---|---|---|
| AZ00-01 | ACCEPTED; 8-page PDF, 3 figures, 7 local tests | No Azure authentication, RBAC query or Provider registration |
| AZ01-01 | ACCEPTED; 7-page PDF, 3 figures, 12 local tests | Synthetic topology only; no Azure availability, SLA or recovery drill |
| AZ02-01 | ACCEPTED; 8-page PDF, 3 figures, 13 local tests; WSL suite 32 tests across 3 directories | Synthetic narrow IPv4 model; no Azure route, NVA or connectivity query |
| AZ02-02 | ACCEPTED; 8-page PDF, 3 figures, 13 local tests; WSL suite 45 tests across 4 directories | Synthetic custom NSG model; no Azure effective-rule or probe query |
| AZ02-03 | ACCEPTED; 11-page PDF, 3 figures, 18 local tests; full Windows and WSL suites each passed 63 tests across 5 directories | Synthetic DNS/access model; no Azure DNS, PE, TLS, Storage or billing query |
| AZ02-04 | ACCEPTED; 9-page PDF, 3 figures, 20 local tests; Windows + WSL suites each passed 83 tests across 6 directories | Synthetic probe contracts and priority candidates only; no Azure health, routing, WAF, TLS, network or billing observation |
| AZ03-01 | ACCEPTED; 9-page PDF, 3 figures, 17 local tests; Windows + WSL suites each passed 100 tests across 7 lab directories | Synthetic token assertions and RBAC fixture only; no JWT, Entra/Azure/Graph query, role change or billing observation |
| AZ03-02 | ACCEPTED; 9-page PDF, 3 figures, 16 local tests; Windows + WSL suites each passed 116 tests across 8 lab directories | Synthetic managed-identity selection, FIC match, token claims, network boolean and Key Vault authorization only; no real token, Azure/network request, vault read, role change or billing observation |
| AZ03-03 | ACCEPTED; 8-page PDF, 3 figures, 16 local tests; Windows + WSL suites each passed 132 tests across 9 lab directories | Synthetic Policy effects, log-visibility classes and Defender effect mapping only; no Azure query, plan enablement, resource operation or billing observation |
| AZ04-01 | ACCEPTED; 6-page PDF, 3 figures, 18 local tests; Windows + WSL suites each passed 150 tests across 10 lab directories | Synthetic VM lifecycle, VMSS rollout, disk cap and boot/app evidence only; Flexible upgrade-policy docs conflict; no Azure query or resource operation |
| AZ04-02 | ACCEPTED; 7-page PDF, 4 figures, 16 local tests; Windows + WSL suites each passed 166 tests across 11 lab directories | Synthetic slot swap, warm-up filter, revision/app-scope separation, readiness policy and traffic rollback; no Azure query or resource operation |
| AZ04-03 | ACCEPTED; 9-page PDF, 5 figures, 21 local tests; Windows + WSL suites each passed 187 tests across 12 lab directories | Synthetic scheduling, scale eligibility, identity matching, ACR authorization, readiness, DNS, PDB and version skew; Docker engine unavailable; no Azure or Kubernetes API operation |
| AZ04-04 | ACCEPTED; 8-page PDF, 5 figures, 28 fixture cases, 30 local tests; Windows + WSL suites each passed 217 tests across 13 lab directories | Synthetic DNS/network/auth/data and recovery selection; no Azure query, Storage/SQL request, restore or billing check |
| AZ05-01 | ACCEPTED; 6-page PDF, 5 figures, 11 fixture cases, 23 local tests; Windows + WSL suites each passed 240 tests across 14 lab directories | Synthetic metrics, aggregation, series, alert events and history gate; no Azure metric/alert/action request or billing check |
| AZ05-02 | ACCEPTED; 7-page PDF, 5 figures, 5 fixture cases, 11 local tests; Windows + WSL suites each passed 251 tests across 15 lab directories | Synthetic workspace-based telemetry, item-count weighting and operation/parent correlation; no KQL/workspace query, telemetry export or billing check |
| AZ05-03 | ACCEPTED; 7-page PDF, 5 figures, 7 synthetic resources, 13 local tests; Windows + WSL suites each passed 264 tests across 16 lab directories | Synthetic scope/readability and offset-pagination drift only; no account/context enumeration, ARM/Resource Graph query, resource mutation or billing check |
| AZ06-01 | ACCEPTED; 7-page PDF, 5 figures, 6 synthetic cases, 16 local tests; Windows + WSL suites each passed 280 tests across 17 lab directories | Synthetic recovery timestamps, integrity, application-probe, isolation and cleanup gates; no Azure Backup/Site Recovery request, restore, resource operation or billing check |
| AZ06-02 | ACCEPTED; 7-page PDF, 5 figures, one synthetic banking incident, 30 local tests; Windows + WSL suites each passed 310 tests across 18 lab directories | Synthetic event/ingestion timeline, competing hypotheses, scoped identity repair, same-probe/data checks; none of the twelve live or eight mandatory local incident contracts is marked complete |
| AZ07-01 | ACCEPTED; 8-page PDF, 5 figures, 26 local model tests; Windows Terraform 1.15.5 init/validate/3 plan-only tests and repository-wide fmt check; Windows + WSL Python suites each passed 336 tests across 19 lab directories | Local built-in terraform_data lab and synthetic reasoning model only; no AzureRM/AzAPI initialization, Azure plan/import, resource operation or billing check; WSL Terraform CLI unavailable |
| AZ07-02 | ACCEPTED; 7-page PDF, 5 figures; actual local State lock contention, provider-specific drift and State recovery; 2 Terraform plan tests; Windows + WSL suites each 336 tests across 19 directories | Windows local backend/file locking and hashicorp/local v2.9.1 only; no Azure Blob lease, AzureRM drift, remote backend or billing check; WSL Terraform CLI unavailable |
| AZ07-03 | ACCEPTED; 7-page PDF, 5 figures; 17 offline YAML/plan-contract tests including 11 negative cases; full Windows + WSL suites each passed 353 tests across 20 lab directories | Generic PyYAML parsing and synthetic plan bytes only; no Azure DevOps server compile/run, WIF, Environment approval, Azure request or billing query |
| AZ08-01 | ACCEPTED; 7-page PDF, 5 figures; 22 local tests; full Windows + WSL suites each passed 375 tests across 21 lab directories | Narrow synthetic contract only; future Azure read-only runbook is NOT_RUN; no Azure request, DNS query, route operation, resource mutation or billing query |
| FIN-01 | PLANNED | Not yet authored or run |

All twenty-two accepted lecture PDFs are independent outputs in textbook/dist/pdf/. Package verification awaits all 23 chapters.
