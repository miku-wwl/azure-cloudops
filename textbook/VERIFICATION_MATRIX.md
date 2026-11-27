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

## Historical starting state before implementation (approved baseline 853ba6c)

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
| AZ07-02 | ACCEPTED; E4 artifact is a 9-page PDF with 6 figures; actual local State lock contention, state-only `terraform_data` import, provider-specific drift, HCL rollback and State recovery; Windows + WSL suites each passed 458 tests across 23 directories | Windows local backend/file locking and `hashicorp/local` v2.9.1 only; no Azure Blob lease, AzureRM drift, remote backend init or billing check; WSL Terraform CLI unavailable |
| AZ07-03 | ACCEPTED; 8-page PDF, 5 figures; E5 pipeline suite passed 29 tests (YAML, plan bundle, plan gate); full Windows + WSL suites each passed 471 tests across 23 lab directories; Terraform 1.15.5 passed fmt, backend-free init/validate in 3 roots and 13 plan-only/mock runs | Generic YAML parsing and synthetic plan bytes/JSON only; no Azure DevOps server compile/run, WIF, approval broker, Azure request or billing query |
| AZ08-01 | ACCEPTED; 9-page PDF, 5 figures; 22 local tests; full Windows + WSL suites each passed 375 tests across 21 lab directories | Narrow synthetic contract only; future Azure read-only runbook is NOT_RUN; no Azure request, DNS query, route operation, resource mutation or billing query |
| FIN-01 | ACCEPTED; 9-page PDF, 5 figures; 27 local tests; full Windows and WSL suites each passed 402 tests across 22 lab directories | Fictional cost ledger and narrow decision contract only; future Cost Management runbook is NOT_RUN; no Azure authentication/query, resource inventory, mutation or billing check |

All twenty-three accepted lecture PDFs are independent outputs in `textbook/dist/pdf/`. Stage 1 B9 package verification passed and is recorded in `RELEASE_ACCEPTANCE.md`; that acceptance covers the Stage 1 publication scope only.

## Stage 2 E3 Terraform engineering (2026-11-27)

| Check | Result | Evidence / limit |
|---|---|---|
| AzureRM/AzAPI config and lockfile | LOCAL_VERIFIED | AzureRM 5.15.0 and AzAPI 2.14.0 installed from Terraform Registry; checked-in lockfile pins provider checksums. No Azure credentials used. |
| Provider registration/auth safety | STATIC_CHECK_PASS + LOCAL_VERIFIED | AzureRM registration `none`; AzAPI `skip_provider_registration=true`; CLI/MSI/OIDC disabled; no resource-provider-registration resource. No Azure registration request. |
| Scope and cost guards | LOCAL_VERIFIED | Empty/off defaults; existing RG only; exact subscription/RG allowlists; AKS node RG allowlist; approval assertion/reference; gross-estimate and 60-minute runtime checks; USD 0.70 line plus USD 0.30 contingency. Controls do not prove owner authorization. |
| Azure Terraform schema and tests | LOCAL_VERIFIED | Windows Terraform 1.15.5 passed `init -backend=false`, `validate`, and 8 mock-provider runs for the Azure root; all runs use `command = plan`, including all categories and negative guard cases. No apply/destroy. |
| All Terraform roots | LOCAL_VERIFIED | Recursive format checks for chapters/terraform plus init/validate/test across three roots; 13 plan-only test runs total. Provider downloads used internet; no Azure API calls. |
| Python regression | LOCAL_VERIFIED | Windows and WSL each passed 429 tests across 23 directories; static contracts check every repository `.tftest.hcl` run is plan-only and directly test environment sanitization. WSL has no Terraform CLI, so Terraform/provider checks ran only on Windows. |
| Chapter/publisher synchronization | LOCAL_VERIFIED | AZ07-01 rebuilt to 9 pages; 11,981 characters; SHA-256 recorded in chapter acceptance; all pages visually reviewed at 88 and 140 DPI. |
| Azure API, spend and billing | NOT_RUN / NOT_VERIFIED | No Azure auth/query, registration, mutation, live plan, pricing check or billing request occurred. Actual cumulative spend is `NOT_VERIFIED`; no live cost estimate is established. |
| Stage 2 release packages | NOT_RUN | Rebuild and byte-verify final PDF/source ZIPs after E4–E10 work. |

## Stage 2 E4 state and controlled delivery (2026-11-27)

| Check | Result | Evidence / limit |
|---|---|---|
| Exact saved-plan approval verifier | LOCAL_VERIFIED | Ed25519 envelope binds Git SHA, environment/scope, provider-lock and plan digests, operation, approver/time, run/approval IDs and one-use nonce; tests cover accept/reject, tamper, expiry, scope, replay, concurrency, failed apply and delete policy. No production signer or trust root. |
| Apply boundary and trust policy | STATIC_CHECK_PASS + LOCAL_VERIFIED | Requires clean checkout and root lockfile; private sealed plan copy; external trust store/digest and control root; rejects CLI/MSI/long-lived credential fallbacks and unsafe plan states. Code checks do not prove protected pipeline configuration. |
| Local delivery tests | LOCAL_VERIFIED | Controlled-apply tests passed 51 cases with one directory-symlink capability skip; Windows/WSL full Python suites each passed 458 tests/23 directories. |
| Terraform/backend checks | LOCAL_VERIFIED | Windows Terraform 1.15.5 recursive fmt, backend-free init/validate and 13 plan-only runs across three roots passed; optional AzureRM OIDC backend example passed `init -backend=false` and `validate`. No remote backend init. |
| AZ07-02 lab and publication | LOCAL_VERIFIED | Actual Windows local lock refusal, state-only import, local drift, config rollback, State backup/restore/destroy; 9-page/6-figure PDF, 12,082 extracted characters, no markers/overflow, 88-DPI review of all pages and 140-DPI review of pages 7–9. SHA-256: `6D26AC6269F2BE33097FE20FCBEC007D283D33A8DC6559739186FEB15D027783`. |
| Azure API, spend and billing | NOT_RUN / NOT_VERIFIED | No Azure auth/query, remote State initialization, resource mutation, network probe, pricing or billing query. Actual cumulative spend remains `NOT_VERIFIED`. |

## Stage 2 E7 incident contracts (2026-11-27)

| Check | Result | Evidence / limit |
|---|---|---|
| Twelve mapped incident contracts | STATIC_CHECK_PASS + LOCAL_VERIFIED | Contract tests verify all 12 IDs, required evidence fields, lecture mapping, explicit live-not-run status and the exact 8 mandatory local IDs. E7 documents contracts only; no incident execution is claimed. |
| Mandatory vs design-only scope | STATIC_CHECK_PASS | IR-01/02/05/07/08/10/11/12 are mandatory for E8; IR-03/04/06/09 remain design-only. E4's local Terraform lab is prior evidence and is not an E8 IR-08 closure. |
| Regression | LOCAL_VERIFIED | Contract suite passed 3 tests; Windows Python 3.13.9 and WSL Python 3.12.3 each passed 510 tests across 24 directories. |
| Cloud, cluster and billing | NOT_RUN / NOT_VERIFIED | No Azure incident/resource mutation, ADO, K8s event query, external target or billing query. Current Docker socket read-only ping did not return; actual spend remains `NOT_VERIFIED`. |

## Stage 2 E6 diagnostics and automation (2026-11-27)

| Check | Result | Evidence / limit |
|---|---|---|
| Resource Graph inventory implementation | LOCAL_VERIFIED | Explicit subscription UUID and optional constrained RG; minimal projection; continuation-token pagination, page/request/retry limits, duplicate/count drift detection, redacted identifiers and distinct exit outcomes; mocked CLI only; no Azure extension/query/login operation. |
| Diagnostic catalog | SOURCE_ANALYSED + LOCAL_VERIFIED | All 13 required categories include purpose, inputs, command examples, interpretation and verification state. All live entries remain `DOCUMENTED_NOT_RUN`; Azure CLI and kubectl were not invoked. |
| Network and token probes | LOCAL_VERIFIED | Six tests exercise bounded DNS waiting, loopback TCP, TLS failure classification, HTTP HEAD, redirect refusal, no body read, and synthetic JWT claim handling. A timed-out OS resolver call may continue in a daemon thread; no external host or token was contacted. |
| Operational KQL library | SOURCE_ANALYSED | Five queries map to published Azure Monitor table schemas and state assumptions/status. No KQL parser, workspace query, or telemetry source was used; all remain `NOT_RUN`. |
| Python regression | LOCAL_VERIFIED | Targeted E6 set passed 36 tests; Windows Python 3.13.9 and WSL Python 3.12.3 each passed 507 tests across 23 directories. |
| PDF synchronization | NOT_REQUIRED | E6 added supplemental tools/query files and lab README/acceptance/source-map entries but did not edit lecture prose or figures; final Stage 2 package refresh remains open. |
| Azure, Kubernetes, DevOps and billing | NOT_RUN / NOT_VERIFIED | No Azure CLI/API/auth, kubectl, ADO, KQL, external endpoint or billing request. Actual cumulative Azure spend remains `NOT_VERIFIED`. |

## Stage 2 E0 independent audit addendum (2026-11-27)

| Area | Evidence | Limit / next gate |
|---|---|---|
| Stage 1 Windows + WSL regression suite | LOCAL_VERIFIED; historical Stage 1 baseline was 402 tests across 22 directories. After E0 corrections, both Windows and WSL pass 407 tests across 22 directories with zero failed directories. | Local Python fixtures and tools only; Azure behavior remains unverified. |
| Terraform static/mock validation | STATIC_CHECK_PASS + LOCAL_VERIFIED; recursive fmt passed, both Terraform roots initialized with `-backend=false`, validated, and passed all five mock contract tests. | Windows Terraform 1.15.5; local/built-in providers only, no Azure provider or API. |
| Corrected PDFs | LOCAL_VERIFIED; AZ02-01 8 pages, FIN-01 9, AZ07-02 7; all 24 affected pages were visually reviewed after rebuild. | Other 20 PDFs retain the separate Stage 1 all-page review records; final Stage 2 package still needs refresh. |
| E2 local test/lab substrate | LOCAL_VERIFIED; bounded shared Python runner passes 418 tests across 23 directories on Windows and WSL; manual SMOKE-LOCAL lifecycle including recovery, reset, owned teardown and empty residual inspection passed. | Synthetic fixture and cleanup harness only; not one of the eight mandatory incident verifications and not Azure/network evidence. Docker Engine unavailable; see `LAB_ENVIRONMENT.md` and `E2_LOCAL_SUBSTRATE.md`. |
| Existing PDF/source ZIPs at audit start | STATIC_CHECK_PASS; 23 PDFs and 289 source files matched byte-for-byte. | Stage 2 corrections change sources; package rebuild and verification are required before the Stage 2 release. |
| Azure claims and live operations | No authentication, subscription query, billing query or resource operation was run during E0. | Actual spend remains `NOT_VERIFIED`; Stage 3 L0 remains outstanding. |
| Cross-stage master-prompt CI/security milestone | PARTIAL; no `.github/workflows` workflow was present at audit start, and the V1 release record does not claim hosted CI or PDF/UA. | Add and execute offline CI and secret scanning; do not infer Milestone A from the narrower Stage 1 B9 acceptance. |
| Independent audit report | COMPLETE for the audited Stage 1 scope and corrected findings; see `E0_INDEPENDENT_AUDIT.md`. | Stage 2 engineering, hosted CI/security, and final package refresh remain separate acceptance gates. |

## Stage 2 E8 local incidents, E9 catalogue and E10 replay (2026-11-26)

| Check | Result | Evidence / limit |
|---|---|---|
| Eight mandatory local incidents | `LOCAL_VERIFIED` | IR-01, IR-02, IR-05, IR-07, IR-08, IR-10, IR-11 and IR-12 ran through real bounded local mechanisms; each captured fault, diagnosis, same-probe recovery and cleanup. See `E8_LOCAL_INCIDENTS.md` and `incidents/evidence/`. |
| Terraform state lock/drift (IR-08) | `LOCAL_VERIFIED` | Competing state-changing local `terraform apply` was rejected by the active lock; local provider drift was reconciled and a final no-change plan recorded. This does not verify Azure Blob leases. |
| Kubernetes image pull (IR-07) | `LOCAL_VERIFIED` | Unique kind cluster produced real kubelet `ErrImagePull`/`ImagePullBackOff` events against a local loopback HTTP 404 fixture; a preloaded image passed the same health probe after recovery. This does not verify AKS/ACR. |
| E9 lab catalogue | STATIC_CHECK_PASS | L0 and all 12 incidents retain all 18 required fields. L0 is complete; per-incident live states remain NOT_RUN. LAB-IR-11 has a proposed region/SKU/resource allowlist and public-price estimate, but is not deployment approval. |
| E10 second clean cycle | `LOCAL_VERIFIED` | `cycle-2` passed all eight incidents; network, permission and data recovery replay checks used fresh or distinct run contexts. `verify_e10.py` confirms required evidence, unchanged Terraform artifacts and cleanup. It is an execution replay, not an independent human review. |
| Current local container host | `LOCAL_VERIFIED` | Docker Engine 29.9.3 responds; existing `argo-canary-local` remained untouched. E8's run-owned kind cluster was removed. |
| Final local Stage 2 checks | `LOCAL_VERIFIED` | Windows Python 3.13.9: 513 tests / 24 directories; Terraform 1.15.5: recursive fmt, backend-free init/validate, 13 plan/mock test runs / 3 roots; Pester 5.7.1: 2 tests passed; repository verifier: 23 lecture mappings, 150 local references and 13 complete E9 cards. No Azure credentials or requests were used. |
| Refreshed Stage 2 packages | `LOCAL_VERIFIED` | PDF ZIP: 23 PDFs, SHA-256 `575F22B9958B68752B54539534E020902135B04BFF22C0BAF0924C8AA0C65608`; source ZIP: 414 files; package verifier confirms byte equality to the source directories. |
| Azure resource operations and billing | L0_READ_ONLY_COMPLETE / NOT_VERIFIED | No project Azure resource mutation. L0 observed one group and three Network Watcher resources; two Cost Management queries returned HTTP 429, so actual billing remains NOT_VERIFIED. |
| Cross-stage hosted CI, security scan and final packages | LOCAL_VERIFIED / HOSTED_PASS | Exact run 45960683857 at 82d7865cc0b4df9ea4ea4eae595a2eaca726441d passed all five jobs. The final acceptance documentation refresh must have its own exact-revision run recorded after publication. |

## Stage 3 L0 read-only Azure preflight (2026-11-26)

| Check | Result | Evidence / limit |
|---|---|---|
| Existing session and context | LIVE_READ_ONLY_PASS | Existing Azure CLI session was Enabled in AzureCloud and remained the default context; no sign-in or context switch. |
| Scope and current-principal role records | PARTIAL_READ_ONLY_PASS | Two assignment records showed Owner as the unique role at subscription scope. Group-derived/effective access was not evaluated; this does not approve a project deployment scope. Identifiers redacted. |
| Visible Azure inventory | LIVE_READ_ONLY_PASS | One resource group and three resources were listable; all three were Microsoft.Network/networkWatchers, each Succeeded. No project lab App Service or lab VNet/NSG/NIC/route table was listed. |
| Provider registration | LIVE_READ_ONLY_PASS | Microsoft.Web and Microsoft.Insights were Registered. No registration or other write occurred. |
| Region/SKU and candidate names | PARTIAL | Subscription supported Australia East, and the read-only Linux F1 location query included it. The earlier 0/2 interpretation from Microsoft.Web regional usage was not an F1 plan count; the official endpoint reports core usage. F1 count, offer entitlement and deployment capacity remain NOT_VERIFIED. The proposed group was absent and site name was available when checked; repeat before use. |
| Cost Management | NOT_VERIFIED | Two read-only Usage queries returned HTTP 429. No billing amount was obtained. Actual cumulative spend remains NOT_VERIFIED. |
| Residual mutation check | LIVE_READ_ONLY_PASS | Final inventory stayed at one group and three Network Watcher resources; no Azure resource was created or changed by this project. |
| IR-11 local Azure package candidate | LOCAL_VERIFIED | Two no-dependency Node 24 LTS ZIP packages were built; local same-probe execution asserted 200 → 500 → 200 and release bodies. Node v26.5.0 was used locally; Azure live state remains NOT_RUN. |
| Live incidents | NOT_RUN | All IR-01 through IR-12 remain unexecuted in Azure. The proposed LAB-IR-11 batch still requires exact owner authorization and run-time cost/offer/plan-limit checks. |
| Final handoff regression and packages (2026-11-26) | `LOCAL_VERIFIED` | Windows Python 3.13.9 passed 515 tests / 24 directories; repository verifier passed 23 curriculum/source/PDF mappings, 154 local Markdown references and 13 complete E9 cards; package verification passed 23 PDFs and 424 source/evidence files. Terraform and Pester gates remain the E10 results above. |
| Stage 3 guard and package refresh (2026-11-27) | `LOCAL_VERIFIED` | Windows Python 3.13.9 passed 528 tests / 24 directories; repository verifier passed 23 mappings, 155 local Markdown references and 13 catalogue cards; Terraform 1.15.5 passed recursive format, backend-free init/validate and 13 mock-plan tests across 3 roots; PowerShell parser passed; package verification passed 23 PDFs and 427 source/evidence files. No Azure request or mutation was made. Exact-revision hosted Pester and Gitleaks checks are recorded by the GitHub Actions run for the published commit. |
| Official KQL demo access (2026-11-27) | `ACCESS_CHECKED / NOT_RUN` | The official Log Analytics demo and ADX help-cluster UI both redirected the unauthenticated browser session to Microsoft sign-in. No credentials were entered and no query was sent; the seven KQL templates remain source-reviewed/not-run. An owner-held identity is required to continue in the no-subscription demo. |
