$ErrorActionPreference = 'Stop'
BeforeAll {
    $script:toolsRoot = Join-Path (Get-Location).Path 'textbook/tools'
    $script:ir11Runner = Join-Path (Get-Location).Path 'textbook/incidents/live_ir11/run_ir11.ps1'
}

Describe 'Offline PowerShell script contract' {
    It 'parses every checked-in tooling PowerShell script' {
        $scripts = @((Get-ChildItem -LiteralPath $script:toolsRoot -Filter '*.ps1' -File) + (Get-Item -LiteralPath $script:ir11Runner))
        $scripts.Count | Should -BeGreaterThan 0

        $parseFailures = foreach ($scriptFile in $scripts) {
            $tokens = $null
            $errors = $null
            [System.Management.Automation.Language.Parser]::ParseFile(
                $scriptFile.FullName,
                [ref]$tokens,
                [ref]$errors
            ) | Out-Null
            foreach ($parseError in $errors) {
                "{0}:{1}: {2}" -f $scriptFile.Name, $parseError.Extent.StartLineNumber, $parseError.Message
            }
        }

        $parseFailures | Should -BeNullOrEmpty
    }

    It 'contains no Azure login, context switch, Terraform apply or destroy command' {
        $scripts = @((Get-ChildItem -LiteralPath $script:toolsRoot -Filter '*.ps1' -File) + (Get-Item -LiteralPath $script:ir11Runner))
        $forbidden = foreach ($scriptFile in $scripts) {
            $tokens = $null
            $errors = $null
            $ast = [System.Management.Automation.Language.Parser]::ParseFile(
                $scriptFile.FullName,
                [ref]$tokens,
                [ref]$errors
            )
            $commands = $ast.FindAll({ param($node) $node -is [System.Management.Automation.Language.CommandAst] }, $true)
            foreach ($command in $commands) {
                $name = $command.GetCommandName()
                $commandArgs = @($command.CommandElements | Select-Object -Skip 1 | ForEach-Object { $_.Extent.Text })
                if (($name -eq 'az' -and (($commandArgs[0] -eq 'login') -or ($commandArgs[0] -eq 'account' -and $commandArgs[1] -eq 'set'))) -or
                    ($name -eq 'terraform' -and $commandArgs[0] -in @('apply', 'destroy'))) {
                    "{0}:{1}: {2} {3}" -f $scriptFile.Name, $command.Extent.StartLineNumber, $name, ($commandArgs -join ' ')
                }
            }
        }

        $forbidden | Should -BeNullOrEmpty
    }
}

Describe 'LAB-IR-11 Azure runbook contract' {
    It 'places approval, price, estimate, and watchdog gates before the first Azure write' {
        $source = Get-Content -LiteralPath $script:ir11Runner -Raw
        $approval = $source.IndexOf("[ValidateSet('LAB-IR-11')]", [StringComparison]::Ordinal)
        $price = $source.IndexOf('if (-not $PriceAndOfferRechecked)', [StringComparison]::Ordinal)
        $limitReview = $source.IndexOf('if (-not $FreePlanLimitRechecked)', [StringComparison]::Ordinal)
        $estimate = $source.IndexOf('if ($EstimatedGrossUsd -ne [decimal]0.00)', [StringComparison]::Ordinal)
        $planLimit = $source.IndexOf('if ($f1PlanCount -ge 10)', [StringComparison]::Ordinal)
        $watchdog = $source.IndexOf('$watchdogProcess = Start-Process', [StringComparison]::Ordinal)
        $firstWrite = $source.IndexOf("'group', 'create'", [StringComparison]::Ordinal)

        $approval | Should -BeGreaterOrEqual 0
        $price | Should -BeGreaterOrEqual 0
        $limitReview | Should -BeGreaterOrEqual 0
        $limitReview | Should -BeLessThan $watchdog
        $estimate | Should -BeGreaterThan $price
        $planLimit | Should -BeGreaterOrEqual 0
        $planLimit | Should -BeLessThan $watchdog
        $watchdog | Should -BeGreaterThan $estimate
        $firstWrite | Should -BeGreaterThan $watchdog
        $source | Should -Match 'run_id = \$runId'
        $source | Should -Match 'Set-Content -LiteralPath \$doneFile'
        $source | Should -Not -Match 'Microsoft\.Web/locations/.*/usages'
        $source | Should -Match 'wait_seconds = 1500'
        $source | Should -Match 'max_runtime_seconds = 2700'
        $source | Should -Match 'AddMinutes\(20\)'
    }

    It 'does not add login or default-subscription switch commands to the runbook' {
        $source = Get-Content -LiteralPath $script:ir11Runner -Raw
        $source | Should -Not -Match "(?i)Invoke-AzChecked\s+@\('login'"
        $source | Should -Not -Match "(?i)Invoke-AzChecked\s+@\('account',\s*'set'"
        $source | Should -Not -Match "(?i)&\s*az\s+(login|account\s+set)"
    }

    It 'passes the Windows name-check JSON through a BOM-free temporary @file and removes it' {
        $source = Get-Content -LiteralPath $script:ir11Runner -Raw
        $writeBody = $source.IndexOf('[System.IO.File]::WriteAllText($nameBodyFile, $nameBody, [System.Text.UTF8Encoding]::new($false))', [StringComparison]::Ordinal)
        $bodyArgument = $source.IndexOf("'--body', `$nameBodyArgument", [StringComparison]::Ordinal)
        $cleanup = $source.IndexOf('Remove-Item -LiteralPath $nameBodyFile -Force -ErrorAction SilentlyContinue', [StringComparison]::Ordinal)

        $writeBody | Should -BeGreaterOrEqual 0
        $bodyArgument | Should -BeGreaterThan $writeBody
        $cleanup | Should -BeGreaterThan $bodyArgument
        $source | Should -Match '\$nameBodyArgument\s*=\s*"@\$nameBodyFile"'
    }
}
