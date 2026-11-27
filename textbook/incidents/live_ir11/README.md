# LAB-IR-11 — App Service release rollback

This runbook prepares a disposable Linux App Service F1 drill. The apps use only Node's built-in HTTP module. The 2026-11-28 attempt provisioned the approved group and F1 plan and stopped before app creation at the plan OS verification gate. Both resources were removed and independently verified absent. [Sanitized run record](../evidence/IR-11_azure-2026-11-28.md).

## Local preparation and verification

From the repository root:

    python textbook/incidents/live_ir11/prepare_packages.py
    python -m unittest -v textbook.incidents.tests.test_ir11_packages
    python -m unittest -v textbook.incidents.tests.test_ir11_watchdog

The builder writes two ZIP files under the ignored `work/azure-cloudops-ir11-packages` directory. Each ZIP has `package.json` and `server.js` at its root. The local package test starts the packaged apps and sends the same `GET /health` probe through 200 → 500 → 200. Watchdog tests use mocked Azure CLI responses only; they never contact Azure.

## Azure scope

The 2026-11-28 approval covered one batch with a dedicated resource group `rg-azure-cloudops-ir11-aue`, one Linux F1 plan `asp-azure-cloudops-ir11-aue`, and one Node 24 LTS app `azcoir11aue261126` in Australia East (`australiaeast`). The application contract is three ZIP deployments to the same endpoint. The cache-disabled HTTPS probe requires 200 → 500 → 200, matching release IDs and the correct `healthy` value.

Scope includes only the group, plan and disposable app. The maximum lifetime is 45 minutes through teardown and residual checks. The budget is a conditional USD 0.00 gross estimate for this batch, a USD 0.30 contingency and a USD 1.00 cumulative ceiling. Both scoped billing queries returned HTTP 200 with no amount. Actual billing remains `BILLING_PENDING`.

## Fail-closed runbook — only after exact owner approval

The [runbook](run_ir11.ps1) runs in PowerShell 7 on Windows. It requires `-ApprovedBatch LAB-IR-11`, the exact approved tenant and subscription IDs, the approved gross estimate, and current price, offer and service-limit attestations. It uses the existing CLI context and a pre-registered Microsoft.Web provider. Before creation it checks offer, group absence, F1 plan count, supported region/runtime and name availability. The name check uses a BOM-free temporary JSON body via Azure CLI's `@file` form and removes it in `finally`. It counts existing F1/Free plans directly because the Microsoft.Web regional usage endpoint reports core usage.

After approval, set these local variables to the exact tenant/subscription covered by the approval. Keep their values out of the repository and logs:

    $subscription = $env:AZURE_CLOUDOPS_APPROVED_SUBSCRIPTION_ID
    $tenant = $env:AZURE_CLOUDOPS_APPROVED_TENANT_ID
    if (-not $subscription -or -not $tenant) { throw 'Approved tenant/subscription are required.' }

Reopen the official F1 and bandwidth pricing pages linked in `L0_READ_ONLY_PREFLIGHT.md` and confirm the current account offer. Reopen Microsoft's subscription and service limits page linked there and confirm the Free-plan regional limit used by the runbook. If any current limit, account-specific offer or gross estimate is not reliable, stop. Then, from the repository root, run the local tests and the batch script:

    python textbook/incidents/live_ir11/prepare_packages.py
    python -m unittest -v textbook.incidents.tests.test_ir11_packages textbook.incidents.tests.test_ir11_watchdog
    .\textbook\incidents\live_ir11\run_ir11.ps1 -ApprovedBatch LAB-IR-11 -SubscriptionId $subscription -TenantId $tenant -EstimatedGrossUsd 0.00 -PriceAndOfferRechecked -FreePlanLimitRechecked

The script enforces a USD 0.00 estimate, a unique run tag, a 20-minute work window and bounded CLI and HTTPS calls. The final plan check reads `properties.reserved` from the [App Service Plans ARM response](https://learn.microsoft.com/en-us/rest/api/appservice/app-service-plans/get?view=rest-appservice-2025-03-01) and requires boolean `true`. It records and asserts the original ZIP's hash before each use. `try/finally` deletes the known resources and checks the subscription-wide inventory for residuals in the group. The watchdog verifies the primary result independently and uses run ownership and exact resource names before any deletion. If the group create result is ambiguous, the watchdog keeps monitoring for late completion through the bounded 45-minute window. It starts cleanup after 25 minutes if the primary process has failed.

The ARM projection correction and local probe/watchdog checks were verified offline after the run. Functional app deployment, HTTP failure and rollback in Azure remain `NOT_RUN`. The earlier approval covers the recorded run only.
