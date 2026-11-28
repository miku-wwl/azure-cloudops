# E4 — Terraform state and controlled delivery acceptance

**Status:** COMPLETE for the offline Stage 2 gate.
**Date:** 2026-11-27 (Pacific/Auckland).
**Azure actions:** None. E4 does not configure or use a production trust root or Azure DevOps Environment.

## Delivered controls

- `textbook/tools/controlled_apply.py` verifies a signed approval envelope before applying a saved Terraform plan. The envelope binds the repository commit, environment, subscription and resource group, provider lockfile digest, exact plan digest, operation, approver identity, approval time and expiry, pipeline run and approval IDs, and a one-use nonce.
- The verifier reads Terraform's plan JSON in memory, checks that the plan is complete and applyable, validates its subscription/resource-group target variables, and classifies resource actions. Delete/replacement plans require a distinct destructive operation and an explicit trust-policy allowlist. Unknown or malformed actions fail closed.
- The executable plan is copied outside the checkout to a private temporary location, hash-checked, and that sealed copy alone is passed to `terraform apply`. A clean Git checkout and the selected root's lockfile are required. Approval material and the persistent control root must also be outside the checkout.
- A same-filesystem atomic scope lock prevents concurrent local applies; a persistent nonce ledger rejects replays and consumes the nonce even if apply fails. This is a local/shared-filesystem mechanism, not a distributed lock service.
- The trust store is external and its digest must be pinned by protected pipeline configuration. Identity, scope and operation allowlists are checked. The tool does not include an approval signer, production trust root, Azure DevOps server-side Environment checks, or distributed lock/replay storage.
- Before apply, the tool rejects long-lived Azure credentials and CLI/MSI fallback, requires workload identity/service-connection context, removes Terraform overrides, and configures the AzureRM backend for Entra ID/OIDC. These checks are local code; they do not prove a production pipeline is protected.
- `textbook/terraform/azure-remote-state-backend/` adds an opt-in AzureRM backend example with OIDC/Entra parameters and placeholders. It requires an existing Storage account/container. Only `init -backend=false` and `validate` were run; remote backend initialization was not run.
- AZ07-02's local state lab now demonstrates built-in `terraform_data` state-only import and configuration rollback. The import does not represent importing an external or cloud object.

## Verification evidence

- `textbook/tools/tests/test_controlled_apply.py` covers successful verification and rejection for missing, expired, altered or replayed approvals; changed commit, scope, lockfile or plan; unauthorized identity/operation; trust-store digest mismatch; signature tampering; concurrency; failure nonce consumption; destructive changes; incomplete plans; and unsafe credential settings. The tools test suite passed 51 cases with one platform-capability skip for directory symlinks.
- Full Python regression passed on Windows Python 3.13.9 and WSL Python 3.12.3: **458 tests across 23 directories on each environment, zero failed directories**. The aggregate includes shared tool tests.
- Windows Terraform 1.15.5 passed recursive formatting checks, backend-free init, validate and all 13 plan-only test runs across the three Terraform roots; the Azure reference root passed 8/8 mock-provider runs. The optional backend example separately passed `init -backend=false` and `validate`. WSL has no Terraform CLI.
- The isolated AZ07-02 lab used Windows Terraform 1.15.5 and `hashicorp/local` 2.9.1. It verified a real local state-lock refusal, state-only `terraform_data` import followed by a zero-diff plan and `state rm`, local-file drift/refresh behavior, configuration rollback, backup/state-push recovery and final destroy. The temporary lab State was removed. This is local Terraform evidence, not Azure Blob lease or AzureRM drift evidence.
- The rebuilt AZ07-02 PDF has 9 pages and 12,082 extracted characters, with no placeholder markers or overflow warnings. It contains six editable SVG figures. All pages were rendered and visually reviewed at 88 DPI; the final experiment pages 7–8 were also reviewed at 140 DPI, and the references page 9 was reviewed at 140 DPI. The page break before the local experiment avoids splitting its heading from its explanation. Final artifact: 1,670,818 bytes; SHA-256 `6D26AC6269F2BE33097FE20FCBEC007D283D33A8DC6559739186FEB15D027783`.

## Scope and limits

- No Azure sign-in, subscription/ARM/Entra/Storage request, Azure provider registration, AzureRM backend initialization, remote plan/import/apply, Azure resource mutation, network probe, pricing lookup or billing query occurred in E4.
- The signature verifier is a local verification component, not a complete secure delivery service. A real deployment still needs independently protected signing, trust-store digest configuration, Azure DevOps approvals/checks and exclusive lock, workload identity permissions, and durable shared nonce/lock storage.
- `terraform_data` import only tests Terraform State CLI behavior. Local filesystem locking and local-file provider behavior do not establish Azure Blob lease or AzureRM resource drift behavior.
- Actual cumulative Azure spend remains `NOT_VERIFIED`; this E4 work establishes no live cost estimate. The project ceiling and planning thresholds remain USD 1.00, USD 0.70, and USD 0.30 reserve.

## Primary references

- [Terraform AzureRM backend](https://developer.hashicorp.com/terraform/language/backend/azurerm) and [Microsoft: store Terraform state in Azure Storage](https://learn.microsoft.com/en-us/azure/developer/terraform/store-state-in-azure-storage).
- [Terraform state locking](https://developer.hashicorp.com/terraform/language/state/locking), [terraform import](https://developer.hashicorp.com/terraform/cli/commands/import), [`terraform_data`](https://developer.hashicorp.com/terraform/language/resources/terraform-data), [saved-plan inspection](https://developer.hashicorp.com/terraform/cli/commands/show), and [Terraform JSON output format](https://developer.hashicorp.com/terraform/internals/json-format).
- [Ed25519 signing and verification](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/).
