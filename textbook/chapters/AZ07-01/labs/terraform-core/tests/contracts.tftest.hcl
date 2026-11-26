run "accept_valid_local_contract" {
  command = plan

  variables {
    environment = "test"
    scope       = "lab/synthetic/resource-group"
  }

  assert {
    condition     = output.resource_contract.provider == "terraform_data (Terraform built-in)"
    error_message = "The lab must use only Terraform's built-in local resource."
  }

  assert {
    condition     = output.release_contract.scope == "lab/synthetic/resource-group"
    error_message = "The module output must preserve the declared local scope."
  }

  assert {
    condition     = output.release_contract.prerequisite_address == "terraform_data.scope_contract"
    error_message = "The downstream contract must identify its declared prerequisite."
  }
}

run "reject_invalid_environment" {
  command = plan

  variables {
    environment = "production"
  }

  expect_failures = [var.environment]
}

run "reject_nonlocal_scope" {
  command = plan

  variables {
    scope = "/subscriptions/example/resourceGroups/real"
  }

  expect_failures = [var.scope]
}
