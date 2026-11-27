[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('LAB-IR-11')]
    [string]$ApprovedBatch,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-fA-F-]{36}$')]
    [string]$SubscriptionId,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-fA-F-]{36}$')]
    [string]$TenantId,

    [Parameter(Mandatory = $true)]
    [decimal]$EstimatedGrossUsd,

    [Parameter(Mandatory = $true)]
    [switch]$PriceAndOfferRechecked,

    [Parameter(Mandatory = $true)]
    [switch]$FreePlanLimitRechecked
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-AzChecked {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $output = & az @Arguments --only-show-errors 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Azure CLI operation failed with exit code $LASTEXITCODE; raw output suppressed."
    }
    return $output
}

function Assert-RunWorkWindow {
    param([Parameter(Mandatory = $true)][DateTimeOffset]$Deadline)
    if ([DateTimeOffset]::UtcNow -ge $Deadline) {
        throw 'The 30-minute work window ended; stop deployment steps and clean up.'
    }
}

if (-not $PriceAndOfferRechecked) {
    throw 'Reopen the official pricing pages and verify the account offer before running this batch.'
}
if (-not $FreePlanLimitRechecked) {
    throw 'Reopen the official Azure subscription and service limits page and verify the regional Free plan limit.'
}
if ($EstimatedGrossUsd -lt [decimal]0 -or $EstimatedGrossUsd -gt [decimal]0.70) {
    throw 'The cumulative gross estimate is invalid or exceeds the USD 0.70 planning threshold.'
}
if ($EstimatedGrossUsd -ne [decimal]0.00) {
    throw 'This approval covers USD 0.00 only; obtain a revised explicit approval for any nonzero estimate.'
}

$context = Invoke-AzChecked @('account', 'show', '--output', 'json') | ConvertFrom-Json
if (
    $context.id -ne $SubscriptionId -or
    $context.tenantId -ne $TenantId -or
    $context.state -ne 'Enabled'
) {
    throw 'The existing default Azure CLI context does not match the approved tenant and subscription.'
}

$resourceGroup = 'rg-azure-cloudops-ir11-aue'
$planName = 'asp-azure-cloudops-ir11-aue'
$siteName = 'azcoir11aue261126'
$location = 'australiaeast'
$projectTag = 'azure-cloudops-ir11'
$runtime = 'NODE:24-lts'

$groupState = Invoke-AzChecked @('group', 'exists', '--name', $resourceGroup, '--subscription', $SubscriptionId, '--output', 'tsv')
if (($groupState | Out-String).Trim() -ne 'false') {
    throw 'The approved resource group already exists or its state is unknown.'
}

$planListText = Invoke-AzChecked @('appservice', 'plan', 'list', '--subscription', $SubscriptionId, '--output', 'json') | Out-String
$planListJson = $planListText.Trim()
if (-not $planListJson.StartsWith('[') -or -not $planListJson.EndsWith(']')) {
    throw 'App Service plan inventory is incomplete; cannot verify the F1 regional plan limit.'
}
try {
    $existingPlans = @($planListJson | ConvertFrom-Json -ErrorAction Stop)
} catch {
    throw 'App Service plan inventory is invalid; cannot verify the F1 regional plan limit.'
}
$regionalF1Plans = @($existingPlans | Where-Object {
    $_.location -ieq $location -and $null -ne $_.sku -and ($_.sku.name -eq 'F1' -or $_.sku.tier -eq 'Free')
})
$f1PlanCount = $regionalF1Plans.Count
if ($f1PlanCount -ge 10) {
    throw 'The documented limit of 10 Free App Service plans per region is already reached; stop.'
}

$runtimeText = Invoke-AzChecked @('webapp', 'list-runtimes', '--os', 'linux', '--output', 'tsv')
if (-not (($runtimeText -split '\r?\n') -contains $runtime)) {
    throw 'NODE:24-lts is not listed; stop.'
}
$locations = Invoke-AzChecked @(
    'appservice', 'list-locations', '--sku', 'F1', '--linux-workers-enabled',
    '--query', "[?name=='Australia East'].name", '--output', 'tsv'
)
if (($locations | Out-String).Trim() -ne 'Australia East') {
    throw 'Linux F1 is not listed in Australia East; stop.'
}

$nameUri = "https://management.azure.com/subscriptions/$SubscriptionId/providers/Microsoft.Web/checknameavailability?api-version=2025-03-01"
$nameBody = @{ name = $siteName; type = 'Microsoft.Web/sites' } | ConvertTo-Json -Compress
$available = Invoke-AzChecked @(
    'rest', '--method', 'post', '--url', $nameUri, '--headers', 'Content-Type=application/json',
    '--body', $nameBody, '--query', 'nameAvailable', '--output', 'tsv', '--subscription', $SubscriptionId
)
if (($available | Out-String).Trim() -ne 'true') {
    throw 'App name is unavailable; obtain a new approval before changing it.'
}

$runId = [guid]::NewGuid().ToString('N')
$workPath = (New-Item -ItemType Directory -Force -Path 'work').FullName
$doneFile = Join-Path $workPath "ir11-$runId.done"
$watchdogConfig = Join-Path $workPath "ir11-$runId-watchdog.json"
$watchdogOut = Join-Path $workPath "ir11-$runId-watchdog.out.log"
$watchdogErr = Join-Path $workPath "ir11-$runId-watchdog.err.log"
[ordered]@{
    subscription_id = $SubscriptionId
    tenant_id = $TenantId
    resource_group = $resourceGroup
    run_id = $runId
    wait_seconds = 1500
    max_runtime_seconds = 2700
    cleanup_timeout_seconds = 600
} | ConvertTo-Json | Set-Content -LiteralPath $watchdogConfig -Encoding utf8

$repoRoot = (Get-Location).Path
$watchdogScript = Join-Path $repoRoot 'textbook/incidents/live_ir11/watchdog.py'
$python = (Get-Command python -CommandType Application -ErrorAction Stop).Source
$watchdogArgs = '"{0}" --config "{1}" --done-file "{2}"' -f $watchdogScript, $watchdogConfig, $doneFile
$watchdogProcess = Start-Process -FilePath $python -ArgumentList $watchdogArgs -WorkingDirectory $repoRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput $watchdogOut -RedirectStandardError $watchdogErr
Start-Sleep -Seconds 1
if ($watchdogProcess.HasExited) {
    throw 'The independent cleanup watchdog did not stay running; no Azure resource was created.'
}

$workDeadline = [DateTimeOffset]::UtcNow.AddMinutes(20)
$appUrl = "https://$siteName.azurewebsites.net/health"

try {
    Assert-RunWorkWindow $workDeadline
    $groupState = Invoke-AzChecked @('group', 'exists', '--name', $resourceGroup, '--subscription', $SubscriptionId, '--output', 'tsv')
    if (($groupState | Out-String).Trim() -ne 'false') {
        throw 'Resource group appeared after preflight; refusing to create or modify it.'
    }
    Invoke-AzChecked @(
        'group', 'create', '--name', $resourceGroup, '--location', $location,
        '--subscription', $SubscriptionId, '--tags', "project=$projectTag", "run-id=$runId", '--output', 'none'
    ) | Out-Null

    $tags = Invoke-AzChecked @('group', 'show', '--name', $resourceGroup, '--subscription', $SubscriptionId, '--query', 'tags', '--output', 'json') | ConvertFrom-Json
    if ($tags.project -ne $projectTag -or $tags.'run-id' -ne $runId) {
        throw 'Run ownership tags were not applied; stop and do not deploy.'
    }

    Assert-RunWorkWindow $workDeadline
    Invoke-AzChecked @(
        'appservice', 'plan', 'create', '--name', $planName, '--resource-group', $resourceGroup,
        '--location', $location, '--sku', 'F1', '--is-linux', '--subscription', $SubscriptionId, '--output', 'none'
    ) | Out-Null
    $plan = Invoke-AzChecked @('appservice', 'plan', 'show', '--name', $planName, '--resource-group', $resourceGroup, '--subscription', $SubscriptionId, '--output', 'json') | ConvertFrom-Json
    if ($plan.location -ne $location -or $plan.sku.name -ne 'F1' -or -not $plan.reserved) {
        throw 'Created plan differs from the approved Linux F1 scope.'
    }

    Assert-RunWorkWindow $workDeadline
    Invoke-AzChecked @(
        'webapp', 'create', '--name', $siteName, '--resource-group', $resourceGroup,
        '--plan', $planName, '--runtime', $runtime, '--subscription', $SubscriptionId, '--output', 'none'
    ) | Out-Null
    $site = Invoke-AzChecked @('webapp', 'show', '--name', $siteName, '--resource-group', $resourceGroup, '--subscription', $SubscriptionId, '--output', 'json') | ConvertFrom-Json
    if ($site.location -ne $location -or $site.kind -notmatch 'linux') {
        throw 'Created web app differs from the approved Linux Australia East scope.'
    }

    python textbook/incidents/live_ir11/prepare_packages.py
    if ($LASTEXITCODE -ne 0) { throw 'Package preparation failed.' }
    Assert-RunWorkWindow $workDeadline
    Invoke-AzChecked @('webapp', 'deploy', '--resource-group', $resourceGroup, '--name', $siteName, '--src-path', 'work/azure-cloudops-ir11-packages/good-v1.zip', '--type', 'zip', '--subscription', $SubscriptionId, '--output', 'none') | Out-Null
    python textbook/incidents/live_ir11/probe.py --url $appUrl --expected-status 200 --expected-release known-good-v1
    if ($LASTEXITCODE -ne 0) { throw 'Known-good baseline probe failed.' }

    Assert-RunWorkWindow $workDeadline
    Invoke-AzChecked @('webapp', 'deploy', '--resource-group', $resourceGroup, '--name', $siteName, '--src-path', 'work/azure-cloudops-ir11-packages/fault-v2.zip', '--type', 'zip', '--subscription', $SubscriptionId, '--output', 'none') | Out-Null
    python textbook/incidents/live_ir11/probe.py --url $appUrl --expected-status 500 --expected-release intentional-failure-v2
    if ($LASTEXITCODE -ne 0) { throw 'Intentional-failure probe did not match.' }

    Assert-RunWorkWindow $workDeadline
    Invoke-AzChecked @('webapp', 'deploy', '--resource-group', $resourceGroup, '--name', $siteName, '--src-path', 'work/azure-cloudops-ir11-packages/good-v1.zip', '--type', 'zip', '--subscription', $SubscriptionId, '--output', 'none') | Out-Null
    python textbook/incidents/live_ir11/probe.py --url $appUrl --expected-status 200 --expected-release known-good-v1
    if ($LASTEXITCODE -ne 0) { throw 'Recovery probe failed.' }
}
finally {
    $stillExists = Invoke-AzChecked @('group', 'exists', '--name', $resourceGroup, '--subscription', $SubscriptionId, '--output', 'tsv')
    if (($stillExists | Out-String).Trim() -eq 'true') {
        $tags = Invoke-AzChecked @('group', 'show', '--name', $resourceGroup, '--subscription', $SubscriptionId, '--query', 'tags', '--output', 'json') | ConvertFrom-Json
        if ($tags.project -ne $projectTag -or $tags.'run-id' -ne $runId) {
            throw 'Ownership tags differ; refusing group deletion. Watchdog will also refuse and report the mismatch.'
        }
        Invoke-AzChecked @('group', 'delete', '--name', $resourceGroup, '--subscription', $SubscriptionId, '--yes', '--output', 'none') | Out-Null
    }
    $stillExists = Invoke-AzChecked @('group', 'exists', '--name', $resourceGroup, '--subscription', $SubscriptionId, '--output', 'tsv')
    if (($stillExists | Out-String).Trim() -ne 'false') {
        throw 'Resource group remains; cleanup is not verified. Independent watchdog remains active.'
    }
    $remainingJson = Invoke-AzChecked @('resource', 'list', '--subscription', $SubscriptionId, '--query', "[?resourceGroup=='$resourceGroup'].id", '--output', 'json')
    $remaining = @($remainingJson | ConvertFrom-Json)
    if ($remaining.Count -ne 0) {
        throw 'Residual resources remain; cleanup is not verified. Independent watchdog remains active.'
    }
    Set-Content -LiteralPath $doneFile -Value 'CLEANED_UP' -Encoding ascii
}

try {
    Wait-Process -Id $watchdogProcess.Id -Timeout 15 -ErrorAction Stop
} catch {
    # The watchdog process remains independent; keep its config and logs for inspection.
}
if ($watchdogProcess.HasExited -and $watchdogProcess.ExitCode -ne 0) {
    throw 'Cleanup watchdog reported an unverified result; inspect its sanitized work/ log.'
}

Write-Output 'LAB-IR-11 run completed; see probe outputs, watchdog log, and cost ledger status.'
