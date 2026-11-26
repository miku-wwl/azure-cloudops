# Terraform CLI local contract lab

This lab uses only the Terraform built-in terraform_data resource. It has no Azure provider, credentials, remote backend, ARM resource ID, apply, or destroy step. The valid local scope is namespaced under lab/.

From the repository root, run:

    terraform -chdir=textbook/chapters/AZ07-01/labs/terraform-core init -backend=false -input=false
    terraform -chdir=textbook/chapters/AZ07-01/labs/terraform-core validate
    terraform -chdir=textbook/chapters/AZ07-01/labs/terraform-core test

The test file evaluates valid module output contracts with plan and expects invalid environment/scope inputs to fail. terraform_data resources represent synthetic contract records; they do not stand for Azure resources. The lab does not verify AzureRM/AzAPI schemas, provider registration, real remote state, Azure access, or cloud plans.
