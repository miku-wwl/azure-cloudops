# Stage 3 L0 — Azure read-only preflight

- Date: 2026-11-26 (Pacific/Auckland)
- Repository: D:/workshop/nov/azure-cloudops
- Mode: existing Azure CLI session only; read operations; no sign-in, subscription switch, resource write or provider registration.

## Observed context and scope

The existing Azure CLI account query succeeded. The context was Enabled in AzureCloud and was already the default; it remained the default at the final inventory check. Tenant, subscription, user and resource identifiers are redacted and were not retained in this report.

A read-only role assignment query for the current principal returned two assignment records. Owner was the unique role name, and both scopes were subscription-level. This establishes assignment records for this principal but does not enumerate group-derived effective access, management-group policy, deny assignments, service-side conditions, or authorize this project’s specific deployment.

The subscription listed one resource group and three resources. All three resources were Microsoft.Network/networkWatchers; each Network Watcher reported Succeeded. No project lab VNet, NSG, route table, NIC, App Service plan or app was present in the listable inventory. Resource visibility remains bounded by the current authorization and API results.

Microsoft.Web and Microsoft.Insights reported Registered. Other read-only checks showed Microsoft.Authorization, Microsoft.ContainerRegistry, Microsoft.ContainerService, Microsoft.Network, Microsoft.Resources and Microsoft.Storage registered. No provider registration occurred.

The subscription location list included Australia East. The read-only App Service location query for Linux SKU F1 included Australia East. The Microsoft.Web regional usage API returned F1 instance currentValue 0 and limit 2 for Australia East (0 of 2 in use). This is a subscription quota reading, not a guarantee of regional deployment capacity. The read-only Linux runtime list returned NODE:26, NODE:24-lts and NODE:22-lts; the candidate uses NODE:24-lts. The candidate dedicated resource group name rg-azure-cloudops-ir11-aue was absent at the time checked. Microsoft.Web name availability check returned true for azcoir11aue261126 at the time checked. Names and capacity may change; repeat before creation.

## Billing and cost

No Cost Management or Consumption CLI extension was installed. The Azure CLI quota extension was not installed; the documented Microsoft.Web usage REST API was queried read-only instead. Two read-only Cost Management Usage API queries at subscription scope returned HTTP 429. No numeric usage result was obtained or retained. Therefore actual Azure billing and actual cumulative spend remain NOT_VERIFIED. A missing or throttled cost view is not evidence of a zero bill.

The project has made no Azure resource changes. This preflight used list/read operations and a resource-name availability check; it did not run Network Watcher diagnostics, Connection Troubleshoot, packet capture, monitoring ingestion, or an application probe.

## Candidate LAB-IR-11 pricing and scope

Microsoft’s current public pricing page lists Linux App Service F1 at USD 0, with shared compute limited to 60 CPU minutes/day, 1 GB RAM and 1 GB storage; the plan is intended for experimentation and learning and has no SLA. The Azure bandwidth pricing page lists the first 100 GB/month of internet egress as free. These public prices, combined with a regional F1 quota reading of 0 used out of 2, support an expected incremental gross estimate of USD 0.00 for one 45-minute F1 app with tiny request/response bodies and no paid dependencies. The bill was not queried successfully, and quota does not guarantee regional capacity. Reconfirm price/offer/quota before any write; stop if the estimate is not reliable, any paid dependency is required, or cumulative estimate exceeds USD 0.70.

Proposed resources, subject to separate owner approval:

| Resource type | Proposed name | Region/SKU | L0 result |
|---|---|---|---|
| Resource group | rg-azure-cloudops-ir11-aue | Australia East scope | Not present when checked |
| Microsoft.Web/serverfarms | asp-azure-cloudops-ir11-aue | Australia East, Linux F1 | Regional F1 quota currentValue 0, limit 2; repeat quota and capacity checks before write |
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
- [Microsoft.Web regional usage REST API](https://learn.microsoft.com/en-us/rest/api/appservice/get-usages-in-location/list?view=rest-appservice-2026-03-15)
- [App Service check-name availability REST API](https://learn.microsoft.com/en-us/rest/api/appservice/check-name-availability/check-name-availability?view=rest-appservice-2025-03-01)
- [Cost Management Usage Query API](https://learn.microsoft.com/en-us/rest/api/cost-management/query/usage)
- [Cost Management work scopes and permissions](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/understand-work-scopes)
- [Network Watcher pricing](https://azure.microsoft.com/en-us/pricing/details/network-watcher/)
