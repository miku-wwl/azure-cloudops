# LAB-IR-11 — App Service release rollback candidate

This is a local, reviewable package for the proposed disposable Azure App Service F1 drill. The packages use the built-in Node HTTP module only; there are no third-party dependencies, telemetry SDKs, log workspaces, secrets or external calls.

## Local preparation and verification

From the repository root:

    python textbook/incidents/live_ir11/prepare_packages.py
    python -m unittest -v textbook/incidents/tests/test_ir11_packages.py

The package builder writes two ZIP files to the ignored work/azure-cloudops-ir11-packages directory. Each ZIP has package.json and server.js at its root, as required for deployment. The local test starts the same packaged apps in sequence and calls GET /health.

## Proposed Azure sequence, only after exact batch approval

Use the approved resource group, F1 plan, site name and Australia East region from LIVE_LAB_CATALOGUE.md. Select the built-in runtime NODE:24-lts. Deploy good-v1.zip and require HTTP 200 plus release=known-good-v1. Deploy fault-v2.zip and require HTTP 500 plus release=intentional-failure-v2. Redeploy the exact same good-v1.zip and require HTTP 200 plus release=known-good-v1. Use the same HTTPS /health probe with cache disabled after each deployment. No production traffic or deployment slot is involved.

## Exact Azure CLI runbook — only after owner approval

This example uses PowerShell and the existing default Azure CLI session. It captures the current subscription ID in a variable and passes it explicitly to every command. It does not log in, change the default context, install extensions, register providers or create any resource until all read-only gates pass.

Build and test the packages before any Azure write:

    python textbook/incidents/live_ir11/prepare_packages.py
    python -m unittest -v textbook/incidents/tests/test_ir11_packages.py

After explicit approval of LAB-IR-11, run the following gate block. It stops unless the proposed group is absent, the candidate site name is still available, Australia East still lists F1/Linux and NODE:24-lts, the Microsoft.Web F1 regional quota has room, and the estimate remains USD 0.00.

    $ErrorActionPreference = 'Stop'
    $subscription = (az account show --query id -o tsv --only-show-errors).Trim()
    if (-not $subscription) { throw 'No current subscription; stop without logging in.' }
    $rg = 'rg-azure-cloudops-ir11-aue'
    $plan = 'asp-azure-cloudops-ir11-aue'
    $site = 'azcoir11aue261126'
    $exists = az group exists --name $rg --subscription $subscription --only-show-errors
    if ($exists -ne 'false') { throw 'The approved resource group already exists or its state is unknown.' }
    $f1uri = "https://management.azure.com/subscriptions/$subscription/providers/Microsoft.Web/locations/australiaeast/usages?api-version=2026-03-15"
    $f1 = @(az rest --method get --url $f1uri --query "value[?name.value=='F1'].{current:currentValue,limit:limit}" -o json --only-show-errors | ConvertFrom-Json)
    if ($f1.Count -ne 1 -or $f1[0].limit -lt 1 -or $f1[0].current -ge $f1[0].limit) { throw 'F1 quota unavailable; stop.' }
    $runtimes = az webapp list-runtimes --os linux -o tsv --only-show-errors
    if ($runtimes -notcontains 'NODE:24-lts') { throw 'NODE:24-lts is not listed; stop.' }
    $locations = az appservice list-locations --sku F1 --linux-workers-enabled --query "[?name=='Australia East'].name" -o tsv --only-show-errors
    if ($locations -ne 'Australia East') { throw 'Linux F1 is not listed in Australia East; stop.' }
    New-Item -ItemType Directory -Force work | Out-Null
    $nameBodyPath = 'work/ir11-name-check.json'
    Set-Content -LiteralPath $nameBodyPath -Value '{"name":"azcoir11aue261126","type":"Microsoft.Web/sites"}' -Encoding utf8
    $nameUri = "https://management.azure.com/subscriptions/$subscription/providers/Microsoft.Web/checknameavailability?api-version=2025-03-01"
    $available = az rest --method post --url $nameUri --headers 'Content-Type=application/json' --body "@$nameBodyPath" --query nameAvailable -o tsv --only-show-errors
    Remove-Item -LiteralPath $nameBodyPath
    if ($available -ne 'true') { throw 'App name is unavailable; request new approval before changing it.' }
    $estimateUsd = [decimal]0.00
    if ($estimateUsd -gt [decimal]0.70) { throw 'Estimated gross cost exceeds the planning threshold; stop.' }

Immediately before a write, reopen the official F1 and bandwidth pricing pages linked from L0_READ_ONLY_PREFLIGHT.md and confirm the estimate is still USD 0.00. The CLI gate cannot fetch a billing quote. If the offer or price changed, stop and get a revised batch approval.

Only after those checks pass, create exactly the approved resource group, one Linux F1 plan and one Node 24 LTS site. Put the following block inside a PowerShell try/finally. Check $LASTEXITCODE after every az and python command; any non-zero result throws and moves to cleanup.

    try {
        az group create --name $rg --location australiaeast --subscription $subscription --output none
        if ($LASTEXITCODE -ne 0) { throw 'Resource group creation failed.' }
        az appservice plan create --name $plan --resource-group $rg --location australiaeast --sku F1 --is-linux --subscription $subscription --output none
        if ($LASTEXITCODE -ne 0) { throw 'F1 plan creation failed.' }
        az webapp create --name $site --resource-group $rg --plan $plan --runtime 'NODE:24-lts' --subscription $subscription --output none
        if ($LASTEXITCODE -ne 0) { throw 'Web app creation failed.' }
        python textbook/incidents/live_ir11/prepare_packages.py
        if ($LASTEXITCODE -ne 0) { throw 'Package preparation failed.' }
        $url = "https://$site.azurewebsites.net/health"
        az webapp deploy --resource-group $rg --name $site --src-path work/azure-cloudops-ir11-packages/good-v1.zip --type zip --subscription $subscription --output none
        if ($LASTEXITCODE -ne 0) { throw 'Known-good deployment failed.' }
        python textbook/incidents/live_ir11/probe.py --url $url --expected-status 200 --expected-release known-good-v1
        if ($LASTEXITCODE -ne 0) { throw 'Baseline probe failed.' }
        az webapp deploy --resource-group $rg --name $site --src-path work/azure-cloudops-ir11-packages/fault-v2.zip --type zip --subscription $subscription --output none
        if ($LASTEXITCODE -ne 0) { throw 'Fault deployment failed.' }
        python textbook/incidents/live_ir11/probe.py --url $url --expected-status 500 --expected-release intentional-failure-v2
        if ($LASTEXITCODE -ne 0) { throw 'Fault probe did not match.' }
        az webapp deploy --resource-group $rg --name $site --src-path work/azure-cloudops-ir11-packages/good-v1.zip --type zip --subscription $subscription --output none
        if ($LASTEXITCODE -ne 0) { throw 'Recovery deployment failed.' }
        python textbook/incidents/live_ir11/probe.py --url $url --expected-status 200 --expected-release known-good-v1
        if ($LASTEXITCODE -ne 0) { throw 'Recovery probe failed.' }
    }
    finally {
        $stillExists = az group exists --name $rg --subscription $subscription --only-show-errors
        if ($LASTEXITCODE -ne 0) { throw 'Cannot verify the approved resource group before cleanup.' }
        if ($stillExists -eq 'true') {
            az group delete --name $rg --subscription $subscription --yes --output none
            if ($LASTEXITCODE -ne 0) { throw 'Resource group cleanup failed; stop all further incidents.' }
        }
        $stillExists = az group exists --name $rg --subscription $subscription --only-show-errors
        if ($LASTEXITCODE -ne 0 -or $stillExists -ne 'false') { throw 'Resource group still exists; stop all further incidents.' }
        $remaining = @(az resource list --subscription $subscription -o json --only-show-errors | ConvertFrom-Json | Where-Object { $_.resourceGroup -eq $rg })
        if ($LASTEXITCODE -ne 0 -or $remaining.Count -ne 0) { throw 'Residual resources remain or inventory is incomplete; stop all further incidents.' }
    }

The runbook’s execution block is not run now. Enforce the 45-minute maximum while it runs, stop on any mismatch or unexpected resource, and do not continue to another incident if recovery, teardown, residual checks or the cost gate fail. The account-specific invoice remains NOT_VERIFIED unless a later billing query succeeds.

The three deployment commands are not run by this package builder. It makes no Azure request. Azure provisioning/deployment remains NOT_RUN until the owner approves the exact batch. After recovery, delete only the app, plan and dedicated resource group created by the run, then query the explicit resource group and subscription inventory for zero residual resources.
