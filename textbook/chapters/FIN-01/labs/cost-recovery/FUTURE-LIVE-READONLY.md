# FIN-01 future Azure observation runbook

**未来授权的只读流程；尚未执行。** 本文描述如何在明确范围内查询成本和资源信息，不执行 Azure 请求或资源变更。

## Authorization and cost gate

Before execution, the owner-approved scope record must name the exact tenant, subscription or billing scope, query purpose, date window, identities, allowed commands, data handling, and owner. The owner must separately authorize that exact read-only batch. Do not infer authorization from this document or the project-wide USD 1.00 resource-mutation ceiling.

The query below uses the Cost Management Query REST API at one explicitly supplied subscription scope. Its POST method submits a read query; it does not create or update a resource. Required access must be confirmed at that exact scope. Microsoft documents the `Microsoft.CostManagement/query/action` operation; a Cost Management Reader role may provide the needed read access, subject to billing agreement and scope. Do not broaden scope to make a failed query work.

This procedure makes no promise about billing data freshness or customer price accuracy. Cost data can be delayed or revised. No live-query cost estimate has been approved; record the source, date and expected effects in the maintenance cost record before execution. Any required paid-resource, export, advisor-refresh, or configuration action is outside this runbook and must stop for a new review.

## Prerequisites

- the owner-approved tenant, scope, identity, commands, and data handling are recorded, plus the separate batch authorization above.
- Azure CLI is already installed and authenticated by the owner for the approved identity. This runbook does not run `az login`, select a tenant, list accounts, or change the active subscription.
- The owner supplies the one approved subscription ID and a Cost Management Reader assignment at that scope. If the scope, identity or permission is uncertain, stop.
- Review the current [Cost Management Query API](https://learn.microsoft.com/en-us/rest/api/cost-management/query/usage) version, request schema, and required operations on execution day. The example below was reviewed on 2026-11-27 and uses API `2026-06-01`; API versions and field support can change.

## Query one subscription

Run only after replacing the placeholder with the exact ID already approved by the owner. The command never enumerates subscriptions. The selected dataset is the current month-to-date usage/actual-cost view, aggregated once by resource group; it does not request amortized cost.

```powershell
$subscriptionId = "<EXACT_OWNER_APPROVED_SUBSCRIPTION_ID>"
if ($subscriptionId -eq "<EXACT_OWNER_APPROVED_SUBSCRIPTION_ID>") {
    throw "Replace the placeholder with the explicitly approved scope."
}

$uri = "https://management.azure.com/subscriptions/$subscriptionId/providers/Microsoft.CostManagement/query?api-version=2026-06-01"
$body = @{
    type = "Usage"
    timeframe = "MonthToDate"
    dataset = @{
        granularity = "None"
        aggregation = @{
            totalCost = @{ name = "PreTaxCost"; function = "Sum" }
        }
        grouping = @(
            @{ type = "Dimension"; name = "ResourceGroup" }
        )
    }
} | ConvertTo-Json -Depth 8 -Compress

az rest --method post --url $uri --headers "Content-Type=application/json" --body $body
```

The result returns `properties.columns` and `properties.rows`; interpret each row using the returned column order and currency. A `204` response or empty rows means no data was returned for that query, not that the subscription has no charges. If the response has `nextLink`, mark the evidence incomplete and stop; do not fetch extra pages without confirming that pagination is in the authorized scope. Retain only the minimum redacted evidence needed for review.

Optional resource-group inventory is a separate read operation. Run only if the exact resource group is also explicitly approved, and only to investigate a charge already surfaced by the cost query:

```powershell
$resourceGroup = "<EXACT_OWNER_APPROVED_RESOURCE_GROUP>"
if ($resourceGroup -eq "<EXACT_OWNER_APPROVED_RESOURCE_GROUP>") {
    throw "Replace the placeholder with the explicitly approved resource group."
}

az resource list --subscription $subscriptionId --resource-group $resourceGroup `
    --query "[].{id:id,type:type,location:location,tags:tags}" --output json
```

This reports a point-in-time ARM inventory. It does not prove whether a meter has stopped billing, whether every dependency is visible, or whether data retention permits deletion. Do not run a delete, update, stop/deallocate, export, recommendation refresh, or cleanup command from this observation runbook.

## Expected checks and diagnosis

1. Record the exact scope, UTC query time, selected timeframe/type, currency, returned column names and whether `nextLink` exists.
2. Reconcile positive charges, credits and net amounts without adding `Usage`/actual and amortized views together. Compare like-for-like date, scope, currency and cost metric.
3. Treat missing tags, resource groups or rows as unknown evidence. Cost records may be delayed, revised, or less granular than the underlying resource list.
4. If access is denied, stop and ask the owner to verify the already-approved scope and role. Do not try another subscription, billing scope, or broader role.
5. If data is stale or empty, preserve the result and wait for the documented refresh window. Do not create an export or enable a feature as a workaround.
6. A resource is only a cleanup candidate after its service owner, dependency graph, backup/retention duty, approved change scope, and residual resources are confirmed in a separately authorized workflow. This runbook performs no recovery or cleanup.

## Evidence and cost record

Store a redacted query transcript and review sheet in the approved evidence store only after authorization. Exclude tenant/subscription IDs, principal IDs, email addresses, full resource IDs, secrets and sensitive tags from public lesson artifacts. Record command count, scope, API version, data window, observed response, currency, pagination state, cost uncertainty, and explicit non-mutations in the project ledger. Billing remains `NOT_VERIFIED` until suitable billing evidence is actually obtained.

The query procedure has not been executed, and this document does not estimate or claim Azure cost. Azure budget alerts are not spending caps; keep the cumulative project ceiling and stop threshold in the separate separate cost and authorization review.
