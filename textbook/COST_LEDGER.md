# Azure cost ledger

- Project cumulative incremental Azure ceiling: USD 1.00.
- Conservative planning threshold: USD 0.70.
- Contingency retained for delayed charges and cleanup: USD 0.30.

| Ledger item | Estimate / status | Evidence |
|---|---:|---|
| Azure resource mutations by this project so far | None performed | Session execution record; no deployment command was run |
| AZ02-03 local model | No Azure API, DNS query, probe or resource call; no project Azure charge from this local run | Windows + WSL offline tests only |
| AZ02-04 local model | No Azure API, DNS query, probe, WAF request, resource call or live traffic; no project Azure charge from this local run | Windows + WSL offline tests only |
| AZ03-01 local model | No Entra token, Azure/Graph API, role query, network call or resource operation; no project Azure charge from this local run | Windows + WSL offline tests only |
| AZ03-02 local model | No Entra/IMDS/OIDC token, Azure/Graph API, Key Vault request, network call, role query/change or resource operation; no project Azure charge from this local run | Windows + WSL offline tests only |
| AZ03-03 local model | No Azure sign-in, subscription/policy/activity query, Defender plan enablement, resource operation or billing request; no project Azure charge from this local run | Windows + WSL offline tests only |
| AZ04-01 local model | No Azure sign-in, VM/VMSS/monitor query, CLI execution, network probe, resource operation or billing request; no project Azure charge from this local run | Windows + WSL offline tests only |
| AZ04-02 local model | No Azure sign-in, subscription query, CLI execution, container, probe, identity-token request, resource operation or billing request; no project Azure charge from this local run | Windows + WSL offline tests only |
| AZ04-03 local model | No Azure sign-in, subscription/CLI request, Kubernetes API request, token, network/DNS probe, resource operation or billing request; no project Azure charge from this local run | Windows + WSL offline tests only; Docker engine unavailable |
| AZ04-04 local model | No Azure sign-in, control/data-plane query, DNS/network probe, Storage or SQL request, restore, resource operation or billing request; no project Azure charge from this local run | Windows + WSL offline tests only |
| AZ05-01 local model | No Azure sign-in, Metrics query, alert/action configuration, notification, resource operation or billing request; no project Azure charge from this local run | Windows + WSL offline tests only |
| AZ05-02 local model | No Azure sign-in, workspace/resource query, telemetry export, resource operation or billing request; no project Azure charge from this local run | Windows + WSL offline tests only |
| AZ05-03 local model | No Azure sign-in, account/context enumeration, ARM list, Resource Graph query, resource operation or billing request; no project Azure charge from this local run | Windows + WSL offline tests only |
| AZ06-01 local model | No Azure sign-in, identity/context enumeration, Backup/Site Recovery request, restore, network probe, resource operation or billing request; no project Azure charge from this local run | Windows + WSL offline tests only; six synthetic cases |
| AZ06-02 local model | No Azure authentication, telemetry/KQL query, identity or role operation, network probe, resource mutation or billing request; no project Azure charge from this local run | Windows + WSL offline tests only; one synthetic incident |
| AZ07-01 local Terraform/model | Built-in terraform_data plan-only tests and synthetic Python model; no Azure provider/API, authentication, remote plan/import, registration or billing request; no project Azure charge from this local run | Windows Terraform v1.15.5; Python 336/19 in Windows and WSL; WSL Terraform CLI unavailable |
| AZ07-02 local Terraform state lab | Local backend, local named-pipe lock coordination, hashicorp/local provider and a disposable file; no Azure backend/provider/API/authentication, Storage request, network probe or billing request; no project Azure charge from this local run | Windows Terraform v1.15.5; actual local lock refusal, file drift/reconcile, state backup/restore and destroy; 336 Python tests/19 dirs on Windows and WSL |
| AZ07-03 Azure Pipelines/WIF lesson | Generic YAML parsing and synthetic plan-contract tests only; no Azure DevOps organization/run, Azure identity, token, provider/backend initialization, subscription, network or billing request; no project Azure charge from this local run | PyYAML 6.0.3; 17 local tests, including tamper/scope/expiry/approval negatives; 353 full-suite tests/20 dirs on Windows and WSL |
| AZ08-01 hybrid connectivity lesson | Synthetic offline lab and PDF only; no Azure authentication, control-plane request, DNS query, route/BGP operation, network probe, resource mutation or billing request; no project Azure charge from this local run | 22 local tests; full Windows and WSL suites each passed 375 tests/21 dirs; future read-only runbook is NOT_RUN and has no live-cost estimate |
| FIN-01 FinOps and cost recovery lesson | Fictional ledger, offline unit tests and PDF only; no Azure authentication, Cost Management query, Advisor request, resource inventory, mutation or billing request | 27 local tests; full Windows and WSL suites each passed 402 tests/22 dirs; future read-only runbook is NOT_RUN and has no live-cost estimate |
| Current cumulative actual Azure spend | NOT_VERIFIED | Billing data has not been queried; do not report USD 0.00 actual |
| Current cumulative gross estimate | Not applicable yet | No live experiment has passed L0 scope, pricing and authorization preflight |
| Remaining ceiling | USD 1.00 nominal; actual headroom unverified | Reconcile gross charges separately from credits and billing |

Before any deployment, add an experiment-specific ledger entry with resource allowlist, official price source and access date, region/SKU, maximum runtime, dependencies, teardown cost, reserved contingency, approving scope, and post-run billing status. Stop if a reliable estimate cannot keep cumulative estimated gross charges at or below USD 0.70. Azure budget alerts are not a hard spending cap.
