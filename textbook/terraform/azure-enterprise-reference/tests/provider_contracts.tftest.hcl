mock_provider "azurerm" {
  mock_resource "azurerm_kubernetes_cluster" {
    defaults = {
      kubelet_identity = [{
        client_id                 = "33333333-3333-3333-3333-333333333333"
        object_id                 = "44444444-4444-4444-4444-444444444444"
        user_assigned_identity_id = "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/rg-azure-cloudops-test/providers/Microsoft.ManagedIdentity/userAssignedIdentities/coops-test-kubelet"
      }]
    }
  }

  mock_resource "azurerm_user_assigned_identity" {
    defaults = {
      client_id    = "55555555-5555-5555-5555-555555555555"
      principal_id = "66666666-6666-6666-6666-666666666666"
      tenant_id    = "22222222-2222-2222-2222-222222222222"
    }
  }
}
mock_provider "azapi" {}

run "defaults_plan_no_azure_resources" {
  command = plan

  assert {
    condition     = output.azure_resources_enabled == false
    error_message = "All Azure resource features must remain disabled by default."
  }

  assert {
    condition     = length(output.enabled_service_categories) == 0
    error_message = "The default plan must not enable any Azure service category."
  }

  assert {
    condition     = output.virtual_network_id == null && output.storage_account_id == null
    error_message = "The default plan must have no Azure resource outputs."
  }
}

run "authorized_fixture_plans_network_with_mock_provider" {
  command = plan

  variables {
    target_subscription_id               = "11111111-1111-1111-1111-111111111111"
    target_resource_group_name           = "rg-azure-cloudops-test"
    target_location                      = "eastus"
    allowed_subscription_ids             = ["11111111-1111-1111-1111-111111111111"]
    allowed_resource_group_names         = ["rg-azure-cloudops-test"]
    resource_name_prefix                 = "coops-test"
    enable_networking                    = true
    live_changes_authorized              = true
    authorization_reference              = "MOCK-PLAN-ONLY-FIXTURE"
    cost_estimate_verified               = true
    estimated_gross_batch_usd            = 0.10
    cumulative_gross_estimate_before_usd = 0.50
    planned_runtime_minutes              = 15
  }

  assert {
    condition     = output.azure_resources_enabled && contains(output.enabled_service_categories, "networking")
    error_message = "The test fixture should plan only the explicitly enabled network category."
  }
}

run "storage_private_endpoint_plan_uses_mock_providers" {
  command = plan

  variables {
    target_subscription_id               = "11111111-1111-1111-1111-111111111111"
    target_resource_group_name           = "rg-azure-cloudops-test"
    target_location                      = "eastus"
    allowed_subscription_ids             = ["11111111-1111-1111-1111-111111111111"]
    allowed_resource_group_names         = ["rg-azure-cloudops-test"]
    resource_name_prefix                 = "coops-test"
    storage_account_name                 = "stcloudopstest01"
    enable_storage                       = true
    live_changes_authorized              = true
    authorization_reference              = "MOCK-PLAN-ONLY-FIXTURE"
    cost_estimate_verified               = true
    estimated_gross_batch_usd            = 0.10
    cumulative_gross_estimate_before_usd = 0.50
    planned_runtime_minutes              = 15
  }

  assert {
    condition     = contains(output.enabled_service_categories, "storage")
    error_message = "The storage module must be present in the explicitly enabled plan."
  }
}

run "azapi_policy_plan_remains_audit_only" {
  command = plan

  variables {
    target_subscription_id               = "11111111-1111-1111-1111-111111111111"
    target_resource_group_name           = "rg-azure-cloudops-test"
    target_location                      = "eastus"
    allowed_subscription_ids             = ["11111111-1111-1111-1111-111111111111"]
    allowed_resource_group_names         = ["rg-azure-cloudops-test"]
    resource_name_prefix                 = "coops-test"
    policy_definition_id                 = "/providers/Microsoft.Authorization/policyDefinitions/11111111-1111-1111-1111-111111111111"
    enable_audit_policy_assignment       = true
    live_changes_authorized              = true
    authorization_reference              = "MOCK-PLAN-ONLY-FIXTURE"
    cost_estimate_verified               = true
    estimated_gross_batch_usd            = 0.10
    cumulative_gross_estimate_before_usd = 0.50
    planned_runtime_minutes              = 15
  }

  assert {
    condition     = azapi_resource.audit_policy_assignment[0].body.properties.enforcementMode == "DoNotEnforce"
    error_message = "The sample AzAPI policy assignment must not enforce a policy."
  }
}

run "all_enterprise_categories_plan_only_with_mocks" {
  command = plan

  variables {
    target_subscription_id               = "11111111-1111-1111-1111-111111111111"
    target_resource_group_name           = "rg-azure-cloudops-test"
    target_location                      = "eastus"
    allowed_subscription_ids             = ["11111111-1111-1111-1111-111111111111"]
    allowed_resource_group_names         = ["rg-azure-cloudops-test", "rg-azure-cloudops-test-nodes"]
    target_tenant_id                     = "22222222-2222-2222-2222-222222222222"
    resource_name_prefix                 = "coops-test"
    storage_account_name                 = "stcloudopstest01"
    ssh_public_key                       = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4f mock-plan-only"
    aks_node_resource_group_name         = "rg-azure-cloudops-test-nodes"
    policy_definition_id                 = "/providers/Microsoft.Authorization/policyDefinitions/11111111-1111-1111-1111-111111111111"
    enable_networking                    = true
    enable_linux_vm                      = true
    enable_aks                           = true
    enable_container_registry            = true
    enable_user_assigned_identity        = true
    enable_key_vault                     = true
    enable_storage                       = true
    enable_monitoring                    = true
    enable_recovery_vault                = true
    enable_audit_policy_assignment       = true
    live_changes_authorized              = true
    authorization_reference              = "MOCK-PLAN-ONLY-FIXTURE"
    cost_estimate_verified               = true
    estimated_gross_batch_usd            = 0.10
    cumulative_gross_estimate_before_usd = 0.50
    planned_runtime_minutes              = 15
  }

  assert {
    condition     = length(output.enabled_service_categories) == 10
    error_message = "The mock plan must include every represented engineering category."
  }

  assert {
    condition     = output.azure_resources_enabled
    error_message = "The plan fixture should show its opt-in status without applying resources."
  }
}

run "reject_unapproved_azure_plan" {
  command = plan

  variables {
    target_subscription_id               = "11111111-1111-1111-1111-111111111111"
    target_resource_group_name           = "rg-azure-cloudops-test"
    target_location                      = "eastus"
    allowed_subscription_ids             = ["11111111-1111-1111-1111-111111111111"]
    allowed_resource_group_names         = ["rg-azure-cloudops-test"]
    resource_name_prefix                 = "coops-test"
    enable_networking                    = true
    authorization_reference              = "MOCK-PLAN-ONLY-FIXTURE"
    cost_estimate_verified               = true
    estimated_gross_batch_usd            = 0.10
    cumulative_gross_estimate_before_usd = 0.50
    planned_runtime_minutes              = 15
  }

  expect_failures = [terraform_data.live_scope_guard]
}

run "reject_scope_outside_exact_allowlist" {
  command = plan

  variables {
    target_subscription_id               = "11111111-1111-1111-1111-111111111111"
    target_resource_group_name           = "rg-azure-cloudops-test"
    target_location                      = "eastus"
    allowed_subscription_ids             = []
    allowed_resource_group_names         = ["rg-azure-cloudops-test"]
    resource_name_prefix                 = "coops-test"
    enable_networking                    = true
    live_changes_authorized              = true
    authorization_reference              = "MOCK-PLAN-ONLY-FIXTURE"
    cost_estimate_verified               = true
    estimated_gross_batch_usd            = 0.10
    cumulative_gross_estimate_before_usd = 0.50
    planned_runtime_minutes              = 15
  }

  expect_failures = [terraform_data.live_scope_guard]
}

run "reject_batch_above_project_planning_line" {
  command = plan

  variables {
    target_subscription_id               = "11111111-1111-1111-1111-111111111111"
    target_resource_group_name           = "rg-azure-cloudops-test"
    target_location                      = "eastus"
    allowed_subscription_ids             = ["11111111-1111-1111-1111-111111111111"]
    allowed_resource_group_names         = ["rg-azure-cloudops-test"]
    resource_name_prefix                 = "coops-test"
    enable_networking                    = true
    live_changes_authorized              = true
    authorization_reference              = "MOCK-PLAN-ONLY-FIXTURE"
    cost_estimate_verified               = true
    estimated_gross_batch_usd            = 0.10
    cumulative_gross_estimate_before_usd = 0.65
    planned_runtime_minutes              = 15
  }

  expect_failures = [terraform_data.live_scope_guard]
}
