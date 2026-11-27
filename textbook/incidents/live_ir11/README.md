# LAB-IR-11 — App Service release rollback candidate

This local, reviewable package prepares a proposed disposable Linux App Service F1 drill. The apps use only Node's built-in HTTP module; there are no third-party dependencies, telemetry SDKs, secrets, or external calls.

## Local preparation and verification

From the repository root:

    python textbook/incidents/live_ir11/prepare_packages.py
    python -m unittest -v textbook.incidents.tests.test_ir11_packages
    python -m unittest -v textbook.incidents.tests.test_ir11_watchdog

The builder writes two ZIP files under the ignored `work/azure-cloudops-ir11-packages` directory. Each ZIP has `package.json` and `server.js` at its root. The local package test starts the packaged apps and sends the same `GET /health` probe through 200 → 500 → 200. Watchdog tests use mocked Azure CLI responses only; they never contact Azure.

## Proposed Azure batch — exact owner approval required

The only proposed batch creates a dedicated resource group `rg-azure-cloudops-ir11-aue`, one Linux F1 plan `asp-azure-cloudops-ir11-aue`, and one Node 24 LTS app `azcoir11aue261126` in Australia East (`australiaeast`). It deploys the known-good package, deterministic HTTP 500 package, then the identical known-good package to the same endpoint. The same cache-disabled HTTPS probe must observe 200 → 500 → 200 with matching release IDs.

No slots, production routes, Application Insights, Log Analytics, Storage, private networking, paid dependencies, or other Azure resources are in scope. The proposed maximum lifetime is 45 minutes from before the first write through teardown and residual checks. The currently approved gross estimate is USD 0.00; any nonzero estimate requires revised owner approval. Keep the USD 0.30 contingency and never exceed the USD 1.00 cumulative project ceiling. Actual account billing remains `NOT_VERIFIED` until a billing query succeeds.

## Fail-closed runbook — only after exact owner approval

The executable runbook is [run_ir11.ps1](run_ir11.ps1). It requires `-ApprovedBatch LAB-IR-11`, the exact approved tenant and subscription IDs, the approved gross estimate, and explicit current-price/account-offer and service-limit confirmation switches. It does not sign in, change the default subscription, install extensions, or register providers. It rechecks the tenant/subscription, dedicated group absence, the documented regional F1 plan count, Linux runtime, regional SKU availability, and app-name availability before creating any resource. A changed tenant, subscription, name, plan limit, region, runtime, price, or estimate stops the run. The regional Microsoft.Web usage endpoint reports core usage and is not treated as an F1 plan-count check.

After approval, set these local variables to the exact tenant/subscription covered by the approval. Keep their values out of the repository and logs:

    $subscription = $env:AZURE_CLOUDOPS_APPROVED_SUBSCRIPTION_ID
    $tenant = $env:AZURE_CLOUDOPS_APPROVED_TENANT_ID
    if (-not $subscription -or -not $tenant) { throw 'Approved tenant/subscription are required.' }

Reopen the official F1 and bandwidth pricing pages linked in `L0_READ_ONLY_PREFLIGHT.md` and confirm the current account offer. Reopen Microsoft's subscription and service limits page linked there and confirm the Free-plan regional limit used by the runbook. If any current limit, account-specific offer or gross estimate is not reliable, stop. Then, from the repository root, run the local tests and the batch script:

    python textbook/incidents/live_ir11/prepare_packages.py
    python -m unittest -v textbook.incidents.tests.test_ir11_packages textbook.incidents.tests.test_ir11_watchdog
    .\textbook\incidents\live_ir11\run_ir11.ps1 -ApprovedBatch LAB-IR-11 -SubscriptionId $subscription -TenantId $tenant -EstimatedGrossUsd 0.00 -PriceAndOfferRechecked -FreePlanLimitRechecked

The script rejects estimates above USD 0.70 and rejects any nonzero estimate because this approval is specifically for USD 0.00. It tags the dedicated resource group with a unique run ID. Its `try/finally` path cleans up and checks for residual resources. Before the first write it also starts a separate hidden Python watchdog. The main operation window is 20 minutes; the watchdog begins cleanup after 25 minutes and continues checking for delayed resource-group creation through a final bounded cleanup window before the 45-minute hard limit. It deletes only a group bearing both the project tag and that run's exact ID, and verifies the group and residual inventory are empty. It remains active after the primary cleanup marker to catch an ARM create request that completes after the CLI call timed out. The primary process writes the watchdog completion marker only after it independently verifies cleanup.

If the primary process exits unexpectedly, the watchdog remains independent. Its config and sanitized logs stay under ignored `work/`. If the current tenant/subscription, ownership tags, deletion, or residual inventory cannot be verified, the run is not complete and no further incident should start. The runbook has not been run against Azure; all live incident statuses remain `NOT_RUN` pending owner approval.
