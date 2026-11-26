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
| Current cumulative actual Azure spend | NOT_VERIFIED | Billing data has not been queried; do not report USD 0.00 actual |
| Current cumulative gross estimate | Not applicable yet | No live experiment has passed L0 scope, pricing and authorization preflight |
| Remaining ceiling | USD 1.00 nominal; actual headroom unverified | Reconcile gross charges separately from credits and billing |

Before any deployment, add an experiment-specific ledger entry with resource allowlist, official price source and access date, region/SKU, maximum runtime, dependencies, teardown cost, reserved contingency, approving scope, and post-run billing status. Stop if a reliable estimate cannot keep cumulative estimated gross charges at or below USD 0.70. Azure budget alerts are not a hard spending cap.
