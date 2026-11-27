# AZ07-03 Azure Pipelines engineering lab

The lab has two deliberately separate pipeline definitions:

- `azure-pipelines.yml` is offline-only. It runs YAML and synthetic plan-contract tests, has `trigger: none`, checks out only `self` with credentials disabled, and contains no Azure task.
- `enterprise-pipeline.yml` is a representative Plan → PlanReview → Apply design. Its compile-time `enableCloudDelivery` parameter defaults to `false`, so the cloud stages are excluded from the expanded graph until someone explicitly enables them. It has not been uploaded, compiled or queued in Azure DevOps.

## What the local tests verify

- `tests/test_pipeline_yaml.py` parses the offline pipeline, enterprise pipeline and reusable stage template as generic YAML. It checks the disabled default, stage order, WIF task/connection references, current-run artifact download, owner-managed resource hooks, exact Terraform version guards and the controlled apply wrapper. PyYAML is not the Azure Pipelines schema compiler; these assertions do not prove that Azure DevOps accepts or runs the template.
- `tests/test_plan_gate.py` runs the original synthetic contract verifier. It accepts one fixture and rejects tampering, wrong source/scope/provider lock/run, expiration, future approval, self-approval, missing timezone and overlong validity.
- `tests/test_plan_bundle.py` runs the new bundle builder/verifier on temporary synthetic bytes and JSON. It checks exact source/run/target/backend/lock/plan binding, resource and output action summaries without values, destructive replacement classification, path boundaries and malformed data. It does not produce or inspect a real Terraform saved plan.
- `python textbook/tools/verify_terraform.py` performs only recursive format, `init -backend=false`, validate and mock-provider plan tests. The AzureRM backend is not initialized against Azure.

Run from the repository root:

```powershell
python -m pip install -r textbook/chapters/AZ07-03/labs/azure-pipelines/requirements.txt
python -m unittest discover -s textbook/chapters/AZ07-03/labs/azure-pipelines/tests -p "test_*.py" -v
python textbook/tools/verify_terraform.py
```

Synthetic plans and manifests are confined to temporary test folders and removed by the fixtures. No saved plan, approval envelope, State file, access token, or trust key is committed.

## External prerequisites before any enterprise pipeline could run

These are organization-owned resources, not files created by this lab:

1. Configure Azure Repos branch Build Validation and protect `main` and any template source. For production, move the enforced policy template to an independent protected repository and use `extends`/Required template checks; this same-repository include is a teaching source, not a tamper-proof policy. Azure Repos PR validation is not configured by YAML `pr:`.
2. Create separate Plan and Apply Azure Resource Manager Service Connections using WIF. Bind issuer/subject/audience to the correct Entra identities, grant only the individual pipeline access, and use different least-privilege Azure roles. Do not grant all pipelines access.
3. Create a PlanReview Environment and an Apply Environment. Resource owners must configure branch control, designated human approvals, self-approval policy, timeouts, required template checks, and an Exclusive lock on the Apply Environment. YAML `lockBehavior: sequential` selects the queue behavior; it does not create the check.
4. Create separate protected Variable Groups. The Plan group supplies nonsecret target metadata; the Apply group supplies the pinned trust-store digest, broker credential if required, and durable `CONTROL_ROOT`. Authorize only this pipeline and avoid Open access.
5. Upload backend `.tfbackend`, target `.tfvars`, and approval trust-store data as owner-managed Secure Files, then restrict their access to this pipeline. The Plan tfvars must explicitly set `use_workload_identity = true` and the authorized, allowlisted target and feature values. Keep all such data outside Git.
6. Provision isolated Plan, Review and Apply pools with the same verified Terraform 1.15.5 and provider lock. The Apply agent must have the compatible Python/`cryptography` runtime, `cloudops-approval-broker`, protected logs, and a persistent access-controlled local `CONTROL_ROOT`. The supplied E4 nonce/lock mechanism is local filesystem coordination; do not share it among several agents or external writers without verifying filesystem semantics or replacing it with a distributed lock/replay service.
7. Implement and independently protect `cloudops-approval-broker`. After Environment checks pass, it must inspect Azure DevOps run/check records, identify the real human decision, validate the exact manifest and destructive-action policy, then issue an E4-compatible short-lived signed envelope. The binary plan and Pipeline Artifact remain sensitive; restrict readers and retention.
8. Confirm one-stage plan/apply permissions for State Blob data access and each planned Azure resource action. The plan identity needs reads for refresh and data sources; Apply needs only the planned writes plus State access. Compute roles from the reviewed graph rather than starting with subscription Contributor.

The template references example resource names; it does not create those resources. The local checks do not validate all Azure YAML schema rules or the broker contract. A production deployment requires a separately authorized Stage 3 batch, with an exact subscription/resource-group/resource allowlist, credible current price estimate at or below the remaining USD 0.70 planning line, and the project USD 1.00 cumulative ceiling. Do not enable or queue the cloud path as part of Stage 2.

## Evidence boundary

No Azure DevOps organization/project was accessed. No pipeline was uploaded, expanded, queued or executed by the Azure DevOps service. No Service Connection, Environment, Variable Group, Secure File, agent pool, Entra credential, token, Azure backend, plan, resource, network probe, billing query or Azure request was created or used. The project’s cumulative actual Azure spend remains `NOT_VERIFIED`.
