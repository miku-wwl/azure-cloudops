# Stage 3 L0 — Azure read-only preflight

- Date: 2026-11-26 (Pacific/Auckland)
- Repository: D:/workshop/nov/azure-cloudops
- Mode: existing Azure CLI session only; read operations; no sign-in, subscription switch, resource write or provider registration.

## Observed context and scope

The existing Azure CLI account query succeeded. The context was Enabled in AzureCloud and was already the default; it remained the default at the final inventory check. Tenant, subscription, user and resource identifiers are redacted and were not retained in this report.

A read-only role assignment query for the current principal returned two assignment records. Owner was the unique role name, and both scopes were subscription-level. This establishes assignment records for this principal but does not enumerate group-derived effective access, management-group policy, deny assignments, service-side conditions, or authorize this project’s specific deployment.

The subscription listed one resource group and three resources. All three resources were Microsoft.Network/networkWatchers; each Network Watcher reported Succeeded. No project lab VNet, NSG, route table, NIC, App Service plan or app was present in the listable inventory. Resource visibility remains bounded by the current authorization and API results.

Microsoft.Web and Microsoft.Insights reported Registered. Other read-only checks showed Microsoft.Authorization, Microsoft.ContainerRegistry, Microsoft.ContainerService, Microsoft.Network, Microsoft.Resources and Microsoft.Storage registered. No provider registration occurred.

The subscription location list included Australia East. The read-only App Service location query for Linux SKU F1 included Australia East. An earlier interpretation recorded the Microsoft.Web regional usage response as F1 instance currentValue 0 and limit 2. Review of Microsoft's API contract shows that this endpoint reports regional core usage, and its documented example is a core-count quota; it does not establish an F1 plan count. Correct the earlier interpretation: subscription F1 plan count, F1 entitlement and regional deployment capacity are NOT_VERIFIED. No Azure query was made during this correction. The read-only Linux runtime list returned NODE:26, NODE:24-lts and NODE:22-lts; the candidate uses NODE:24-lts. The candidate dedicated resource group name was absent at the time checked. Microsoft.Web name availability check returned true for azcoir11aue261126 at the time checked. Names, entitlement and capacity may change; repeat before creation.

## Billing and cost

No Cost Management or Consumption CLI extension was installed. The Azure CLI quota extension was not installed. The Microsoft.Web regional usage REST API was queried read-only, but it reports core usage and cannot establish the F1 plan count. Two read-only Cost Management Usage API queries at subscription scope returned HTTP 429. No numeric usage result was obtained or retained. Therefore actual Azure billing and cumulative spend remain NOT_VERIFIED. The initial F1 inventory was not sufficient; a later subscription-wide inventory is recorded in the 2026-11-27 recheck below. Account offer entitlement and regional deployment capacity remain NOT_VERIFIED. A missing or throttled cost view is not evidence of a zero bill.

The project has made no Azure resource changes. This preflight used list/read operations and a resource-name availability check; it did not run Network Watcher diagnostics, Connection Troubleshoot, packet capture, monitoring ingestion, or an application probe.

## Stage 3 read-only recheck — 2026-11-27

The existing Azure CLI context was still Enabled in AzureCloud and remained the default. No sign-in, context switch, extension installation, provider registration or resource mutation occurred. Read-only checks returned:

- The subscription-wide App Service plan inventory contained **0 visible F1 / Free plans in Australia East** at the time queried. The runbook repeats this inventory and stops if the documented limit of 10 per region has been reached. This count does not establish account offer entitlement or deployment capacity.
- `NODE:24-lts` remained in the Linux runtime list, and the Linux F1 location list still included Australia East.
- `rg-azure-cloudops-ir11-aue` was absent (`az group exists` returned `false`).
- The candidate site name `azcoir11aue261126` was available. The first PowerShell inline-JSON `az rest` attempt returned HTTP 400 because the request body was empty; the check succeeded when the same JSON was supplied through Azure CLI's documented `@file` convention. The temporary file was removed. The runbook now uses a uniquely named, BOM-free `work/` file and deletes it in `finally`.

These are time-bound observations, not provisioning approval. Recheck every condition immediately before a write. Account entitlement, current deployment capacity and actual Azure billing remain **NOT_VERIFIED**. The HTTP 429 cost-query result remains the latest billing evidence.

## Candidate A governance reads — 2026-11-27

Using the same existing default session and explicit subscription scope, the CLI returned 996 role definitions, 3,760 policy definitions (2,928 `BuiltIn`, 832 `Static`; no `Custom` entries in this result), and 2 policy assignments at the subscription scope. These are definition/assignment inventory counts, not an evaluation of effective permissions or inherited policy. A seven-day Activity Log request returned its capped sample of 10 events, all in the `Administrative` category; the cap prevents treating that sample as a complete event inventory. No names, principal IDs, subscription IDs or event details were retained.

The subscription's management-group list command returned exit code 1 with provider auto-registration explicitly disabled, so hierarchy membership was not established and no provider was registered. `Microsoft.ResourceGraph` reported `Registered`, but the Resource Graph CLI extension is absent and no Resource Graph data query was run. The documented Resource Graph REST query endpoint is a POST request; the attempted CLI invocation was blocked by local command policy before execution, so no request reached Azure. These gaps remain unverified; the earlier ARM inventory remains the only resource inventory used. All executed calls in this snapshot were reads and made no Azure resource changes.

## Stage 3 subscription and CLI recheck — 2026-11-28

The existing Azure CLI account remained logged in, Enabled in AzureCloud, and on its existing default subscription. A read-only Azure Resource Manager subscription GET returned `quotaId=AzureForStudents_2018-01-01` and `spendingLimit=On`; raw subscription and tenant IDs were not retained. Microsoft's spending-limit documentation says this limit prevents spending past the subscription credit and can disable deployed services after the credit is exhausted. It is an account credit control, not the project's USD 1.00 cumulative ceiling, and it does not establish App Service F1 eligibility or remaining credit. See [Subscriptions - Get REST API](https://learn.microsoft.com/en-us/rest/api/resources/subscriptions/get?view=rest-resources-2022-12-01) and [Azure spending limit](https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/spending-limit).

A current read-only App Service plan inventory returned 0 visible F1 plans, and `az appservice list-locations --sku F1 --linux-workers-enabled` still included Australia East. Microsoft's Linux App Service pricing page, checked on 2026-11-28, lists F1 under the Free plan with shared compute limited to 60 CPU minutes/day, 1 GB RAM and 1 GB storage; it describes the free plan as intended for experimentation and learning with no SLA. The page cautions that prices are estimates and actual pricing can vary by offer. These observations do not prove account eligibility or deployment capacity; repeat the applicable checks before any approved write. Cost Management still has no successful amount result, so actual Azure billing remains **NOT_VERIFIED**.

`Microsoft.ResourceGraph` remained Registered, but the Resource Graph CLI extension was absent. Installing `resource-graph` failed before any Resource Graph query: Azure CLI 2.86.0's pip child process could not load the bundled Python 3.13.13 `pyexpat` module (`ImportError: DLL load failed while importing pyexpat`). `az extension list` remained empty. The subscription-policy read above succeeded through the existing CLI session and direct read-only ARM GET; no default subscription switch was made. No Resource Graph query reached Azure, no provider registration occurred, and no Azure resource changed. This is a local Azure CLI Python/runtime issue, not evidence of missing Azure authorization.

## Candidate LAB-IR-11 pricing and scope

Microsoft’s Linux App Service pricing page, checked on 2026-11-28, lists F1 under the Free plan with shared compute limited to 60 CPU minutes/day, 1 GB RAM and 1 GB storage; the plan is intended for experimentation and learning and has no SLA. The Azure bandwidth pricing page lists the first 100 GB/month of internet egress as free. These public terms support only a conditional USD 0.00 gross estimate for one 45-minute F1 app with tiny request/response bodies, if the account offer permits F1 and no paid dependency is required; Microsoft's pricing page notes that actual pricing may vary by offer. The 2026-11-28 subscription inventory showed 0 visible F1/Free plans in Australia East, and the subscription quota ID is Azure for Students, but neither observation proves F1 eligibility or regional capacity. Actual billing was not queried successfully. Reconfirm current pricing, account offer, the documented regional Free-plan limit and app-name availability before any write; stop if the estimate is not reliable, any paid dependency is required, or cumulative estimate exceeds USD 0.70.

Proposed resources, subject to separate owner approval:

| Resource type | Proposed name | Region/SKU | L0 result |
|---|---|---|---|
| Resource group | rg-azure-cloudops-ir11-aue | Australia East scope | Not present when checked |
| Microsoft.Web/serverfarms | asp-azure-cloudops-ir11-aue | Australia East, Linux F1 | 0 visible F1/Free plans in the 2026-11-28 subscription inventory; the Azure for Students quota ID does not prove F1 eligibility or regional capacity. The prior 0/2 interpretation is invalid as F1 plan evidence. |
| Microsoft.Web/sites | azcoir11aue261126 | Australia East, Linux F1 app | Name availability returned true when checked; repeat before write |

The proposed run has a 45-minute maximum including diagnosis, recovery, teardown and residual checks. Its two no-dependency release packages and local probe test are in incidents/live_ir11; the local test ran with Node v26.5.0, while the current Azure CLI runtime list includes the selected Node 24 LTS stack. It deploys a known-good package, a deterministic HTTP 500 package and the same known-good package to the same disposable app endpoint. It uses the same probe for baseline/fault/recovery, no slots or production traffic, no paid telemetry, no Storage account, no private endpoint, no other Azure resource, and deletes only the approved app, plan and dedicated group. Any unapproved dependency or cost changes stop the run.

This is a concrete candidate, not authorization. Exact owner approval is still required for this resource allowlist and operation. All Azure incident statuses IR-01 through IR-12 remain NOT_RUN.

## Primary sources

- [App Service Linux pricing](https://azure.microsoft.com/en-us/pricing/details/app-service/linux/)
- [Azure bandwidth pricing](https://azure.microsoft.com/en-au/pricing/details/bandwidth/)
- [App Service hosting plans](https://learn.microsoft.com/en-us/azure/app-service/overview-hosting-plans)
- [ZIP deployment for App Service](https://learn.microsoft.com/en-us/azure/app-service/deploy-zip)
- [Configure Node.js apps in App Service](https://learn.microsoft.com/en-us/azure/app-service/configure-language-nodejs)
- [App Service quotas and metrics](https://learn.microsoft.com/en-us/azure/app-service/web-sites-monitor)
- [Azure subscription and service limits](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits)
- [Microsoft.Web regional usage REST API](https://learn.microsoft.com/en-us/rest/api/appservice/get-usages-in-location/list?view=rest-appservice-2026-03-15)
- [App Service check-name availability REST API](https://learn.microsoft.com/en-us/rest/api/appservice/check-name-availability/check-name-availability?view=rest-appservice-2025-03-01)
- [Cost Management Usage Query API](https://learn.microsoft.com/en-us/rest/api/cost-management/query/usage)
- [Cost Management work scopes and permissions](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/understand-work-scopes)
- [Network Watcher pricing](https://azure.microsoft.com/en-us/pricing/details/network-watcher/)
- [Azure Resource Graph REST query API](https://learn.microsoft.com/en-us/rest/api/azureresourcegraph/resourcegraph/resources/resources?view=rest-azureresourcegraph-resourcegraph-2024-04-01)
- [Subscriptions - Get REST API](https://learn.microsoft.com/en-us/rest/api/resources/subscriptions/get?view=rest-resources-2022-12-01)
- [Azure spending limit](https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/spending-limit)
