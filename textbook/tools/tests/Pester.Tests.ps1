$ErrorActionPreference = 'Stop'
BeforeAll {
    $script:toolsRoot = Join-Path (Get-Location).Path 'textbook/tools'
}

Describe 'Offline PowerShell script contract' {
    It 'parses every checked-in tooling PowerShell script' {
        $scripts = @(Get-ChildItem -LiteralPath $script:toolsRoot -Filter '*.ps1' -File)
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
        $forbidden = foreach ($scriptFile in Get-ChildItem -LiteralPath $script:toolsRoot -Filter '*.ps1' -File) {
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
