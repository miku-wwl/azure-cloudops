#Requires -Version 7.0
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

$azPath = (Get-Command az -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$azPrefix = @()
if ([IO.Path]::GetExtension($azPath) -in @('.cmd', '.bat')) {
    $azPath = Join-Path (Split-Path (Split-Path $azPath -Parent) -Parent) 'python.exe'
    if (-not (Test-Path -LiteralPath $azPath -PathType Leaf)) { throw 'Azure CLI bundled interpreter is unavailable.' }
    $azPrefix = @('-IBm', 'azure.cli')
}
$script:azDeadline = [DateTimeOffset]::UtcNow.AddMinutes(6)

function Invoke-BoundedProcess {
    param([string]$File, [string[]]$Arguments, [int]$Seconds, [string]$Operation)

    if ($Seconds -lt 1) { throw "Deadline reached before $Operation." }
    $start = [Diagnostics.ProcessStartInfo]::new($File)
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $start.StandardOutputEncoding = [Text.Encoding]::UTF8
    $start.StandardErrorEncoding = [Text.Encoding]::UTF8
    foreach ($argument in $Arguments) { $start.ArgumentList.Add($argument) }
    $process = [Diagnostics.Process]::Start($start)
    try {
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit(1000 * $Seconds)) {
            if (-not $process.HasExited) { $process.Kill($true) }
            throw "$Operation exceeded its bounded timeout. Azure may still be processing the request."
        }
        return @{
            ExitCode = $process.ExitCode
            Output = $stdout.GetAwaiter().GetResult()
            Error = $stderr.GetAwaiter().GetResult()
        }
    } finally {
        $process.Dispose()
    }
}

function Invoke-AzChecked {
    param([Parameter(Mandatory = $true)][string[]]$Arguments, [int]$TimeoutSeconds = 55)

    $operation = 'az ' + ($Arguments[0..1] -join ' ')
    $remaining = [Math]::Floor(($script:azDeadline - [DateTimeOffset]::UtcNow).TotalSeconds)
    $result = Invoke-BoundedProcess $azPath ($azPrefix + $Arguments + '--only-show-errors') ([int][Math]::Min($TimeoutSeconds, $remaining)) $operation
    if ($result.ExitCode -ne 0) {
        $code = [regex]::Match($result.Error, '(?m)^(?:Code:\s*|ERROR:\s*\()([A-Za-z][A-Za-z0-9_.-]{0,79})').Groups[1].Value
        $reason = if ($code) { $code } else { 'unclassified' }
        throw "$operation failed (exit $($result.ExitCode), code $reason)."
    }
    return $result.Output.Trim()
}

function Assert-RunWorkWindow {
    param([Parameter(Mandatory = $true)][DateTimeOffset]$Deadline)
    if ([DateTimeOffset]::UtcNow -ge $Deadline) {
        throw 'The 20-minute work window ended; stop deployment steps and clean up.'
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
    $context.state -ne 'Enabled' -or $context.environmentName -ne 'AzureCloud' -or -not $context.isDefault
) {
    throw 'The existing default Azure CLI context does not match the approved tenant and subscription.'
}

$resourceGroup = 'rg-azure-cloudops-ir11-aue'
$planName = 'asp-azure-cloudops-ir11-aue'
$siteName = 'azcoir11aue261126'
$location = 'australiaeast'
$projectTag = 'azure-cloudops-ir11'
$runtime = 'NODE:24-lts'
$scope = "/subscriptions/$SubscriptionId/resourceGroups/$resourceGroup/providers/Microsoft.Web"
$planId = "$scope/serverfarms/$planName"
$siteId = "$scope/sites/$siteName"

$offer = Invoke-AzChecked @(
    'rest', '--method', 'get', '--url', "https://management.azure.com/subscriptions/${SubscriptionId}?api-version=2022-12-01",
    '--subscription', $SubscriptionId, '--output', 'json'
) | ConvertFrom-Json
if ($offer.state -ne 'Enabled' -or $offer.tenantId -ne $TenantId -or $offer.subscriptionPolicies.quotaId -ne 'AzureForStudents_2018-01-01') {
    throw 'The approved Azure for Students offer could not be verified.'
}
$provider = Invoke-AzChecked @('provider', 'show', '--namespace', 'Microsoft.Web', '--subscription', $SubscriptionId, '--query', 'registrationState', '--output', 'tsv')
if ($provider -ne 'Registered') { throw 'Microsoft.Web is not already registered.' }

function Get-RunResourceIds {
    $raw = Invoke-AzChecked @('resource', 'list', '--subscription', $SubscriptionId, '--query', "[?resourceGroup=='$resourceGroup'].id", '--output', 'json')
    if (-not $raw.StartsWith('[')) { throw 'The residual inventory did not return a list.' }
    $raw | ConvertFrom-Json
}

function Get-SubscriptionInventory {
    $resources = Invoke-AzChecked @('resource', 'list', '--subscription', $SubscriptionId, '--query', 'sort_by([].{id:id,type:type,location:location,tags:tags}, &id)', '--output', 'json')
    $groups = Invoke-AzChecked @('group', 'list', '--subscription', $SubscriptionId, '--query', 'sort_by([].{id:id,location:location,tags:tags}, &id)', '--output', 'json')
    if (-not $resources.StartsWith('[') -or -not $groups.StartsWith('[')) { throw 'The subscription inventory did not return lists.' }
    return @{ Resources = $resources; Groups = $groups }
}

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

$runtimeText = Invoke-AzChecked @('webapp', 'list-runtimes', '--os', 'linux', '--subscription', $SubscriptionId, '--output', 'tsv')
if (-not (($runtimeText -split '\r?\n') -contains $runtime)) {
    throw 'NODE:24-lts is not listed; stop.'
}
$locations = Invoke-AzChecked @(
    'appservice', 'list-locations', '--sku', 'F1', '--linux-workers-enabled',
    '--subscription', $SubscriptionId, '--query', "[?name=='Australia East'].name", '--output', 'tsv'
)
if (($locations | Out-String).Trim() -ne 'Australia East') {
    throw 'Linux F1 is not listed in Australia East; stop.'
}

$nameUri = "https://management.azure.com/subscriptions/$SubscriptionId/providers/Microsoft.Web/checknameavailability?api-version=2025-03-01"
$nameBody = @{ name = $siteName; type = 'Microsoft.Web/sites' } | ConvertTo-Json -Compress
$preflightWorkPath = Join-Path (Get-Location).Path 'work'
$null = New-Item -ItemType Directory -Force -Path $preflightWorkPath
$nameBodyFile = Join-Path $preflightWorkPath "ir11-name-check-$([guid]::NewGuid().ToString('N')).json"
$nameBodyArgument = "@$nameBodyFile"
try {
    [System.IO.File]::WriteAllText($nameBodyFile, $nameBody, [System.Text.UTF8Encoding]::new($false))
    $available = Invoke-AzChecked @(
        'rest', '--method', 'post', '--url', $nameUri, '--headers', 'Content-Type=application/json',
        '--body', $nameBodyArgument, '--query', 'nameAvailable', '--output', 'tsv', '--subscription', $SubscriptionId
    )
} finally {
    Remove-Item -LiteralPath $nameBodyFile -Force -ErrorAction SilentlyContinue
}
if (($available | Out-String).Trim() -ne 'true') {
    throw 'App name is unavailable; obtain a new approval before changing it.'
}

$runId = [guid]::NewGuid().ToString('N')
$workPath = (New-Item -ItemType Directory -Force -Path 'work').FullName
$doneFile = Join-Path $workPath "ir11-$runId.done"
$watchdogConfig = Join-Path $workPath "ir11-$runId-watchdog.json"
$watchdogOut = Join-Path $workPath "ir11-$runId-watchdog.out.log"
$watchdogErr = Join-Path $workPath "ir11-$runId-watchdog.err.log"
$packagePath = Join-Path $workPath "ir11-$runId-packages"
$goodZip = Join-Path $packagePath 'good-v1.zip'
$faultZip = Join-Path $packagePath 'fault-v2.zip'
$repoRoot = (Get-Location).Path
$python = (Get-Command python -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$prepared = Invoke-BoundedProcess $python @('textbook/incidents/live_ir11/prepare_packages.py', '--out', $packagePath) 30 'local package build'
if ($prepared.ExitCode -ne 0) { throw 'Local package preparation failed.' }
$goodHash = (Get-FileHash -LiteralPath $goodZip -Algorithm SHA256).Hash
$faultHash = (Get-FileHash -LiteralPath $faultZip -Algorithm SHA256).Hash
Write-Host "packages_verified good_sha256=$goodHash fault_sha256=$faultHash"
$before = Get-SubscriptionInventory

[ordered]@{
    subscription_id = $SubscriptionId
    tenant_id = $TenantId
    resource_group = $resourceGroup
    run_id = $runId
    wait_seconds = 1500
    max_runtime_seconds = 2700
    cleanup_timeout_seconds = 600
} | ConvertTo-Json | Set-Content -LiteralPath $watchdogConfig -Encoding utf8

$watchdogScript = Join-Path $repoRoot 'textbook/incidents/live_ir11/watchdog.py'
$watchdogArgs = '"{0}" --config "{1}" --done-file "{2}"' -f $watchdogScript, $watchdogConfig, $doneFile
$cleanupDeadline = [DateTimeOffset]::UtcNow.AddMinutes(45)
$watchdogProcess = Start-Process -FilePath $python -ArgumentList $watchdogArgs -WorkingDirectory $repoRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput $watchdogOut -RedirectStandardError $watchdogErr
Start-Sleep -Seconds 1
if ($watchdogProcess.HasExited) {
    throw 'The independent cleanup watchdog did not stay running; no Azure resource was created.'
}

$workDeadline = [DateTimeOffset]::UtcNow.AddMinutes(20)
$script:azDeadline = $workDeadline
$groupCreateAttempted = $false
$groupCreateCompleted = $false
$timer = [Diagnostics.Stopwatch]::StartNew()

function Write-RunEvent {
    param([string]$Event)
    Write-Host ('{0} elapsed_s={1:F2} {2}' -f [DateTimeOffset]::UtcNow.ToString('o'), $timer.Elapsed.TotalSeconds, $Event)
}

function Invoke-ReleaseStep {
    param([string]$Zip, [string]$Sha256, [int]$Status, [string]$Release)

    Assert-RunWorkWindow $workDeadline
    if ((Get-FileHash -LiteralPath $Zip -Algorithm SHA256).Hash -cne $Sha256) {
        throw 'A deployment package no longer matches the preflight SHA-256.'
    }
    Write-RunEvent "deployment_start release=$Release sha256=$Sha256"
    Invoke-AzChecked @(
        'webapp', 'deploy', '--resource-group', $resourceGroup, '--name', $siteName, '--src-path', $Zip,
        '--type', 'zip', '--clean', 'true', '--restart', 'true', '--async', 'false', '--track-status', 'false',
        '--timeout', '150000', '--subscription', $SubscriptionId, '--output', 'none'
    ) 160 | Out-Null
    Write-RunEvent "deployment_completed release=$Release"
    $probeBudget = [int][Math]::Min(90, [Math]::Floor(($workDeadline - [DateTimeOffset]::UtcNow).TotalSeconds) - 2)
    if ($probeBudget -lt 1) { throw 'No time remains for the release probe.' }
    $probe = Invoke-BoundedProcess $python @(
        'textbook/incidents/live_ir11/probe.py', '--url', $appUrl, '--expected-status', "$Status",
        '--expected-release', $Release, '--wait-seconds', "$probeBudget"
    ) ($probeBudget + 2) 'HTTPS health probe'
    if ($probe.ExitCode -ne 0) {
        Write-RunEvent $probe.Error.Trim()
        throw "The health probe did not verify release $Release."
    }
    Write-RunEvent $probe.Output.Trim()
}

try {
    Assert-RunWorkWindow $workDeadline
    $groupState = Invoke-AzChecked @('group', 'exists', '--name', $resourceGroup, '--subscription', $SubscriptionId, '--output', 'tsv')
    if (($groupState | Out-String).Trim() -ne 'false') {
        throw 'Resource group appeared after preflight; refusing to create or modify it.'
    }
    $groupCreateAttempted = $true
    Write-RunEvent 'group_create_started'
    Invoke-AzChecked @(
        'group', 'create', '--name', $resourceGroup, '--location', $location,
        '--subscription', $SubscriptionId, '--tags', "project=$projectTag", "run-id=$runId", '--output', 'none'
    ) 90 | Out-Null
    $groupCreateCompleted = $true
    Write-RunEvent 'group_created'

    $tags = Invoke-AzChecked @('group', 'show', '--name', $resourceGroup, '--subscription', $SubscriptionId, '--query', 'tags', '--output', 'json') | ConvertFrom-Json
    if ($tags.project -ne $projectTag -or $tags.'run-id' -ne $runId) {
        throw 'Run ownership tags were not applied; stop and do not deploy.'
    }
    if (@(Get-RunResourceIds).Count -ne 0) { throw 'The dedicated group already contains an unexpected resource.' }

    Assert-RunWorkWindow $workDeadline
    Invoke-AzChecked @(
        'appservice', 'plan', 'create', '--name', $planName, '--resource-group', $resourceGroup,
        '--location', $location, '--sku', 'F1', '--is-linux', '--subscription', $SubscriptionId, '--output', 'none'
    ) 120 | Out-Null
    Write-RunEvent 'plan_created requested_sku=F1 requested_os=Linux'
    $plan = Invoke-AzChecked @(
        'rest', '--method', 'get', '--url', "https://management.azure.com${planId}?api-version=2025-03-01",
        '--subscription', $SubscriptionId, '--query', '{id:id,location:location,sku:sku.name,tier:sku.tier,linux:properties.reserved}', '--output', 'json'
    ) | ConvertFrom-Json
    if ($plan.id -ne $planId -or ($plan.location -replace '\s', '') -ne $location -or $plan.sku -ne 'F1' -or $plan.tier -ne 'Free') {
        throw 'The App Service Plans REST response did not confirm the approved F1 scope.'
    }
    if ($plan.linux -isnot [bool] -or -not $plan.linux) { throw 'The App Service Plans REST response did not confirm properties.reserved=true. Stop before creating the app.' }
    Write-RunEvent 'plan_verified sku=F1 tier=Free os=Linux'

    Assert-RunWorkWindow $workDeadline
    Invoke-AzChecked @(
        'webapp', 'create', '--name', $siteName, '--resource-group', $resourceGroup,
        '--plan', $planId, '--runtime', $runtime, '--startup-file', 'node server.js', '--https-only', 'true',
        '--subscription', $SubscriptionId, '--output', 'none'
    ) 120 | Out-Null
    $site = Invoke-AzChecked @(
        'rest', '--method', 'get', '--url', "https://management.azure.com${siteId}?api-version=2025-03-01",
        '--subscription', $SubscriptionId, '--query', '{id:id,location:location,kind:kind,serverFarmId:properties.serverFarmId,httpsOnly:properties.httpsOnly,defaultHostName:properties.defaultHostName}', '--output', 'json'
    ) | ConvertFrom-Json
    if ($site.id -ne $siteId -or ($site.location -replace '\s', '') -ne $location -or $site.kind -notmatch 'linux' -or $site.serverFarmId -ne $planId -or -not $site.httpsOnly) {
        throw 'Created web app differs from the approved Linux Australia East scope.'
    }
    $effectiveRuntime = Invoke-AzChecked @(
        'rest', '--method', 'get', '--url', "https://management.azure.com${siteId}/config/web?api-version=2025-03-01",
        '--subscription', $SubscriptionId, '--query', 'properties.linuxFxVersion', '--output', 'tsv'
    )
    $children = @(Get-RunResourceIds)
    if (($effectiveRuntime -replace '[^a-z0-9]', '') -ne 'NODE24lts' -or $children.Count -ne 2 -or $planId -notin $children -or $siteId -notin $children) {
        throw 'The effective runtime or the dedicated resource inventory differs from the approved scope.'
    }
    if ($site.defaultHostName -cnotmatch ('^' + [regex]::Escape($siteName) + '(?:-[a-z0-9-]+)?(?:\.[a-z0-9-]+)*\.azurewebsites\.net$')) {
        throw 'ARM did not report the expected default app hostname.'
    }
    $appUrl = "https://$($site.defaultHostName)/health"
    Write-RunEvent 'app_verified runtime=NODE:24-lts https_only=true approved_resource_count=2'

    Invoke-ReleaseStep $goodZip $goodHash 200 'known-good-v1'
    Invoke-ReleaseStep $faultZip $faultHash 500 'intentional-failure-v2'
    Write-RunEvent 'regression_observed source=fault-v2.zip cause=release_health_handler_returns_500'
    Invoke-ReleaseStep $goodZip $goodHash 200 'known-good-v1'
} catch {
    Write-RunEvent "experiment_stopped $($_.Exception.Message)"
    throw
}
finally {
    $script:azDeadline = $cleanupDeadline
    $stillExists = Invoke-AzChecked @('group', 'exists', '--name', $resourceGroup, '--subscription', $SubscriptionId, '--output', 'tsv')
    if (($stillExists | Out-String).Trim() -eq 'true') {
        $tags = Invoke-AzChecked @('group', 'show', '--name', $resourceGroup, '--subscription', $SubscriptionId, '--query', 'tags', '--output', 'json') | ConvertFrom-Json
        if ($tags.project -ne $projectTag -or $tags.'run-id' -ne $runId) {
            throw 'Ownership tags differ; refusing group deletion. Watchdog will also refuse and report the mismatch.'
        }
        $children = @(Get-RunResourceIds)
        if (@($children | Where-Object { $_ -notin @($siteId, $planId) }).Count -ne 0) {
            throw 'Refusing cleanup of a group containing a resource outside the approved scope.'
        }
        try {
            if ($siteId -in $children) {
                Invoke-AzChecked @('webapp', 'delete', '--name', $siteName, '--resource-group', $resourceGroup, '--subscription', $SubscriptionId, '--keep-empty-plan', '--output', 'none') 120 | Out-Null
                Write-RunEvent 'app_deleted'
            }
            if ($planId -in $children) {
                Invoke-AzChecked @('appservice', 'plan', 'delete', '--name', $planName, '--resource-group', $resourceGroup, '--subscription', $SubscriptionId, '--yes', '--output', 'none') 120 | Out-Null
                Write-RunEvent 'plan_deleted'
            }
        } catch {
            Write-RunEvent "individual_delete_incomplete $($_.Exception.Message)"
        }
        Invoke-AzChecked @('group', 'delete', '--name', $resourceGroup, '--subscription', $SubscriptionId, '--yes', '--output', 'none') 420 | Out-Null
        Write-RunEvent 'group_deleted'
    }
    $stillExists = Invoke-AzChecked @('group', 'exists', '--name', $resourceGroup, '--subscription', $SubscriptionId, '--output', 'tsv')
    if (($stillExists | Out-String).Trim() -ne 'false') {
        throw 'Resource group remains; cleanup is not verified. Independent watchdog remains active.'
    }
    $remaining = @(Get-RunResourceIds)
    if ($remaining.Count -ne 0) {
        throw 'Residual resources remain; cleanup is not verified. Independent watchdog remains active.'
    }
    $marker = if ($groupCreateCompleted -or -not $groupCreateAttempted) { 'CLEANED_UP_NO_PENDING_GROUP_CREATE' } else { 'CLEANED_UP' }
    Set-Content -LiteralPath $doneFile -Value $marker -Encoding ascii
    Write-RunEvent 'cleanup_verified group_exists=false residual_count=0'
    $after = Get-SubscriptionInventory
    if ($before.Resources -cne $after.Resources -or $before.Groups -cne $after.Groups) {
        throw 'The unrelated subscription inventory differs from the preflight snapshot.'
    }
    Write-RunEvent 'unrelated_subscription_inventory_unchanged=true'
}

try {
    Wait-Process -Id $watchdogProcess.Id -Timeout 60 -ErrorAction Stop
} catch {
    # The watchdog process remains independent; keep its config and logs for inspection.
}
if ($watchdogProcess.HasExited -and $watchdogProcess.ExitCode -ne 0) {
    throw 'Cleanup watchdog reported an unverified result; inspect its sanitized work/ log.'
}

Write-Output 'LAB-IR-11 run completed; see probe outputs, watchdog log, and cost ledger status.'
