# AZ07-03 offline Azure Pipelines lab

This small lab exercises the YAML files and an exact-plan approval contract without an Azure DevOps organization, Service Connection, Azure identity, Terraform plan, State file, or cloud request.

## What the checks prove

- `test_pipeline_yaml.py` parses the repository YAML with the pinned PyYAML version and checks its offline-only trigger, checkout and reusable-template shape. This is generic YAML parsing plus local assertions, not Azure Pipelines schema validation.
- `test_plan_gate.py` runs the actual `scripts/plan_gate.py` verifier against temporary synthetic bytes. It covers plan tampering, wrong source/scope/provider-lock/run, an expired plan, creator self-approval, missing timezone and future approval.
- The `approval.json` in these tests is a trusted synthetic fixture supplied to the verifier. The verifier does not establish who produced an approval record; a real deployment must rely on protected Azure DevOps resources/checks and a trusted approval/audit source.

The YAML pipeline has `trigger: none`, checks out only `self` without persisting credentials, and contains no Azure task, `terraform apply`, or `terraform destroy`. For Azure Repos, configure PR validation as a target-branch Build validation policy. The named `CloudOps-Offline` agent pool is an organization-side prerequisite if this example is ever run in Azure DevOps; this project has not created or configured it.

## Run locally

From the repository root:

```powershell
python -m pip install -r textbook/chapters/AZ07-03/labs/azure-pipelines/requirements.txt
python -m unittest discover -s textbook/chapters/AZ07-03/labs/azure-pipelines/tests -p "test_*.py" -v
```

All plan bytes and JSON contracts are created in a temporary directory and removed by the test fixture. No raw plan or State file is committed.
