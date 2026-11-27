# Publishing and capture tools

The build, style, SVG figure, page-review, image-normalization and window-capture components in this directory are adapted from the AWS CloudOps textbook at commit b44160ea0f864ce7edf40cc0edb402cb53687a63. The source repository is licensed under Apache License 2.0; this adaptation retains that attribution. The Azure repository's original LICENSE remains unchanged. AWS chapter content and experiments are not reused as Azure evidence.

## Build one chapter

From the repository root, run:

    python textbook/tools/build.py AZ00-01

The command generates editable SVGs from the chapter's figures/figs.py, converts Markdown with Pandoc, applies the shared print stylesheet, prints PDF through installed headless Edge, and produces page-review sheets and a QA report in that chapter's ignored build directory.

The output path is textbook/dist/pdf/<id>_<slug>.pdf. A build and automated report do not equal complete visual acceptance: render and inspect every final page, inspect significant figures and dense code at readable scale, correct defects, then rebuild and inspect the affected pages again.

## Review and package

    python textbook/tools/pages.py path/to/chapter.pdf path/to/review 66
    python textbook/tools/package.py
    python textbook/tools/package.py --verify

The collection package is accepted only with exactly 23 PDFs. The source package includes editable sources and Terraform dependency lock files, and excludes build directories, provider caches, local-only redaction maps, raw state and plans. Optional local secret-pattern scans use tools/sensitive.local.txt, which is ignored by Git.

The publisher writes `textbook/dist/publication-manifest.json` alongside the ZIPs. `--verify` checks both archive sizes and SHA-256 values, unique members, and every entry against its on-disk payload. Source text uses LF for the comparison.

## Local lab lifecycle harness (E2)

Run the local-only harness from the repository root:

```powershell
python textbook/tools/labctl.py preflight --target-scope local
$run = python textbook/tools/labctl.py setup --target-scope local | ConvertFrom-Json
$runDir = $run.run_dir
python textbook/tools/labctl.py baseline --target-scope local --run-dir $runDir
python textbook/tools/labctl.py test --target-scope local --run-dir $runDir
python textbook/tools/labctl.py inject --target-scope local --run-dir $runDir
python textbook/tools/labctl.py diagnose --target-scope local --run-dir $runDir
python textbook/tools/labctl.py recover --target-scope local --run-dir $runDir
python textbook/tools/labctl.py test --target-scope local --run-dir $runDir
python textbook/tools/labctl.py residual --target-scope local --run-dir $runDir
python textbook/tools/labctl.py teardown --target-scope local --run-dir $runDir --confirm-run-id $run.run_id
```

All commands require the explicit `local` target. The harness uses a deterministic synthetic fixture under a new, tool-owned temporary directory; it makes no network request, launches no child process, and implements no Azure operation. Teardown requires the exact run ID, a healthy fixture and a clean file list. Unknown files are reported as residuals and preserved. `SMOKE-LOCAL` validates lifecycle and cleanup mechanics only; it is not one of the eight mandatory incident experiments and is not evidence of Azure or network behavior.

Run the cross-platform Python test aggregate with `python textbook/tools/test_python.py`; `bash textbook/tools/test_all.sh --python` calls the same runner in WSL. Every test directory runs in a separate process with a five-minute timeout. Shared tests live in `tools/tests/` and are included in the aggregate.

## Terraform checks (E3)

The opt-in Azure reference is at `textbook/terraform/azure-enterprise-reference/`; reusable modules are in `textbook/terraform/modules/`. Run `python textbook/tools/verify_terraform.py` or `bash textbook/tools/test_all.sh --terraform`. The runner discovers test roots from `*.tftest.hcl`, checks recursive Terraform formatting, then runs backend-free init, validate, and mock-provider tests. It strips `ARM_*`, `AZURE_*`, and `TF_*` child environment values, disables CLI/OIDC/MSI authentication, and uses a temporary empty CLI config. It does not call Azure CLI or execute apply/destroy. Registry downloads are required for provider schema and test verification.

Every test block in the Azure reference uses `command = plan`, mock providers, and fake scope identifiers. Azure feature flags default off. Provider registration is disabled for AzureRM and AzAPI. See `../terraform/azure-enterprise-reference/README.md` for exact scope, cost, and cleanup limits.

## State and controlled delivery (E4)

`../chapters/AZ07-02/labs/terraform-state/scripts/verify_lab.py` reproduces the genuine local lifecycle, built-in `terraform_data` import, local backend lock contention, local-file drift, HCL configuration rollback, state recovery, and destroy sequence inside a bounded temporary copy. Its import case changes only the local State address; it does not import a cloud object. See the lab README for its exact boundary.

`controlled_apply.py` applies only a sealed copy of a saved Terraform plan after checking the clean Git SHA, exact Azure target variables, provider lock digest, plan digest, Ed25519 signature, trusted key-set digest, signer identity/operation policy, approval time, run ID, nonce, and a same-filesystem target lock. The approval, trust store, plan artifact, and persistent control directory must be outside the checkout. The private signing key and protected key-set digest must come from a separate trusted release service. The CLI requires workload identity federation and rejects long-lived credentials; it does not create or configure the approval service, Azure DevOps Environment checks, or a distributed replay/lock service.

Install its Python dependency with `python -m pip install -r textbook/tools/requirements-controlled-apply.txt`. Unit tests use temporary generated keys and a synthetic plan-JSON fixture. They do not invoke Terraform apply or Azure. Terraform `show -json` can expose sensitive State/Plan values, so the production verifier parses it in memory and must not print it. For a distributed Azure DevOps deployment, configure the Environment approval and exclusive-lock checks server-side and use durable shared replay protection; the local directory lock is not distributed.

`../terraform/azure-enterprise-reference/` now declares an empty AzureRM backend for the optional Azure Pipelines template; an owner-managed `.tfbackend` secure file supplies the existing account/container/key, and `use_workload_identity` remains `false` unless the protected tfvars file opts in. `../terraform/azure-remote-state-backend/` remains a minimal teaching sample. Both require an existing state account/container and have not been initialized against Azure. Do not run remote `terraform init` without a separately authorized Stage 3 scope.

## Diagnostics and inventory (E6)

`azure_inventory.py` is a bounded read-only Resource Graph inventory. It requires an explicit subscription UUID on every query page, uses `az graph` when the extension is installed, and otherwise uses the built-in `az rest` query endpoint with the same explicit subscription scope. It never installs the extension, changes the CLI default subscription, or runs login. It follows continuation tokens, bounds page size/count, retries transient failures, and reports authentication, permission, timeout, dependency, and incomplete outcomes separately. Identifiers are SHA-256 references by default; the query does not request resource tags or dynamic properties. REST request bodies use a short-lived `@file` and are removed after each request. It uses the existing Azure CLI session only when an operator explicitly runs it. Local unit tests use mocked responses and do not authenticate or query Azure.

`diagnostics/README.md` and `diagnostic_catalog.json` cover 13 DNS, route, TCP/TLS, NSG, Private Endpoint, identity, token audience, RBAC, Key Vault, Policy, Kubernetes image-pull, application health, and monitoring diagnostics. `network_probe.py` uses a bounded caller wait for DNS and races direct connections to resolved addresses within a connection deadline; an OS resolver call cannot be cancelled and may continue in a daemon thread after timeout. HTTPS validates the certificate, and unauthenticated HTTP HEAD neither follows redirects nor reads a body. `token_audience.py` inspects a token supplied via hidden input but does not acquire it or verify its signature. These checks use loopback and synthetic inputs only; no live Azure, Kubernetes, token, KQL or external-host observation is claimed.

Five additional KQL templates live in `../chapters/AZ05-02/labs/telemetry-triage/queries/`. They state table/column assumptions and remain `NOT_RUN` against a real workspace. See `E6_DIAGNOSTICS_AUTOMATION.md` for evidence and limits.

## Azure Portal captures

Capture only an existing owner-authorized browser session and navigate read-only. Do not create resources, save configuration, enable a paid service or change identity/tenant settings. Use console_prep.js only as a visual redaction aid; review the resulting image before it enters the chapter. The script redacts Azure resource paths, GUIDs, email addresses and IP addresses and supports additional local substitutions through window.__AZURE_REDACTIONS__. Do not place live replacement values in tracked files. Never claim a screenshot is genuine unless it was actually captured from the interface.
