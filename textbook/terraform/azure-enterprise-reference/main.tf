resource "terraform_data" "live_scope_guard" {
  input = {
    any_azure_feature_enabled = local.any_azure_feature_enabled
    target_subscription_id    = var.target_subscription_id
    target_resource_group     = var.target_resource_group_name
    authorization_reference   = var.authorization_reference
    enabled_categories        = local.enabled_categories
  }

  lifecycle {
    precondition {
      condition     = !local.any_azure_feature_enabled || var.live_changes_authorized
      error_message = "Azure resources are disabled unless the owner has authorized this exact batch."
    }

    precondition {
      condition     = !local.any_azure_feature_enabled || trimspace(var.authorization_reference) != ""
      error_message = "An auditable authorization/change reference is required when any Azure feature is enabled."
    }

    precondition {
      condition     = !local.any_azure_feature_enabled || (can(regex("^[0-9a-fA-F-]{36}$", var.target_subscription_id)) && local.subscription_is_allowlisted)
      error_message = "The exact target subscription must be present in allowed_subscription_ids."
    }

    precondition {
      condition     = !local.any_azure_feature_enabled || (can(regex("^rg-azure-cloudops-[a-z0-9-]{1,40}$", var.target_resource_group_name)) && local.target_rg_is_allowlisted)
      error_message = "The existing target resource group must match the local naming contract and exact allowlist."
    }

    precondition {
      condition     = !local.any_azure_feature_enabled || trimspace(var.target_location) != ""
      error_message = "An explicit Azure region is required for an enabled batch."
    }

    precondition {
      condition     = !local.any_azure_feature_enabled || (var.cost_estimate_verified && var.estimated_gross_batch_usd > 0 && var.cumulative_gross_estimate_before_usd + var.estimated_gross_batch_usd <= 0.70 && var.cumulative_gross_estimate_before_usd + var.estimated_gross_batch_usd + 0.30 <= 1.00)
      error_message = "A verified gross cost estimate must fit below USD 0.70, leaving USD 0.30 contingency within the USD 1.00 project cap."
    }

    precondition {
      condition     = !local.any_azure_feature_enabled || (var.planned_runtime_minutes > 0 && var.planned_runtime_minutes <= 60)
      error_message = "An enabled batch requires an explicit runtime from 1 to 60 minutes."
    }

    precondition {
      condition     = !var.enable_linux_vm || (trimspace(var.resource_name_prefix) != "" && trimspace(var.ssh_public_key) != "")
      error_message = "The private Linux VM requires a resource-name prefix and SSH public key."
    }

    precondition {
      condition     = !var.enable_aks || (trimspace(var.resource_name_prefix) != "" && can(regex("^rg-azure-cloudops-[a-z0-9-]{1,40}$", var.aks_node_resource_group_name)) && contains(var.allowed_resource_group_names, var.aks_node_resource_group_name) && var.aks_node_resource_group_name != var.target_resource_group_name)
      error_message = "AKS requires a distinct, explicitly allowlisted node resource group. Azure creates resources there."
    }

    precondition {
      condition     = !var.enable_aks || var.enable_user_assigned_identity
      error_message = "AKS requires the explicitly managed user-assigned identity used by its kubelet."
    }

    precondition {
      condition     = !var.enable_container_registry || trimspace(var.resource_name_prefix) != ""
      error_message = "Container Registry creation requires resource_name_prefix."
    }

    precondition {
      condition     = !var.enable_user_assigned_identity || trimspace(var.resource_name_prefix) != ""
      error_message = "Managed Identity creation requires resource_name_prefix."
    }

    precondition {
      condition     = !var.enable_key_vault || (var.enable_user_assigned_identity && trimspace(var.resource_name_prefix) != "" && can(regex("^[0-9a-fA-F-]{36}$", var.target_tenant_id)))
      error_message = "Key Vault requires an enabled user-assigned identity, tenant UUID, and resource-name prefix."
    }

    precondition {
      condition     = !var.enable_storage || (trimspace(var.resource_name_prefix) != "" && can(regex("^[a-z0-9]{3,24}$", var.storage_account_name)))
      error_message = "Storage creation requires a resource-name prefix and globally unique compliant account name."
    }

    precondition {
      condition     = !var.enable_monitoring || trimspace(var.resource_name_prefix) != ""
      error_message = "Monitoring creation requires resource_name_prefix."
    }

    precondition {
      condition     = !var.enable_recovery_vault || trimspace(var.resource_name_prefix) != ""
      error_message = "Recovery Services Vault creation requires resource_name_prefix."
    }

    precondition {
      condition     = !var.enable_audit_policy_assignment || (can(regex("^/providers/Microsoft.Authorization/policyDefinitions/[^/]+$", var.policy_definition_id)) && trimspace(var.resource_name_prefix) != "")
      error_message = "The audit policy requires a full existing policy definition ID and resource-name prefix."
    }
  }
}

module "network" {
  source = "../modules/network"
  count  = local.network_required ? 1 : 0

  name_prefix         = var.resource_name_prefix
  resource_group_name = var.target_resource_group_name
  location            = var.target_location
  tags                = var.common_tags

  depends_on = [terraform_data.live_scope_guard]
}

module "linux_vm" {
  source = "../modules/linux_vm"
  count  = var.enable_linux_vm ? 1 : 0

  name_prefix         = var.resource_name_prefix
  resource_group_name = var.target_resource_group_name
  location            = var.target_location
  subnet_id           = try(module.network[0].workload_subnet_id, "")
  admin_username      = var.ssh_admin_username
  ssh_public_key      = var.ssh_public_key
  tags                = var.common_tags

  depends_on = [terraform_data.live_scope_guard]
}

module "aks" {
  source = "../modules/aks"
  count  = var.enable_aks ? 1 : 0

  name_prefix              = var.resource_name_prefix
  resource_group_name      = var.target_resource_group_name
  node_resource_group_name = var.aks_node_resource_group_name
  location                 = var.target_location
  subnet_id                = try(module.network[0].aks_subnet_id, "")
  kubelet_identity_id      = try(module.user_assigned_identity[0].id, "")
  tags                     = var.common_tags

  depends_on = [terraform_data.live_scope_guard, azurerm_role_assignment.aks_registry_pull]
}

module "container_registry" {
  source = "../modules/container_registry"
  count  = var.enable_container_registry ? 1 : 0

  name_prefix         = var.resource_name_prefix
  resource_group_name = var.target_resource_group_name
  location            = var.target_location
  subnet_id           = try(module.network[0].private_endpoint_subnet_id, "")
  virtual_network_id  = try(module.network[0].virtual_network_id, "")
  tags                = var.common_tags

  depends_on = [terraform_data.live_scope_guard]
}

module "user_assigned_identity" {
  source = "../modules/user_assigned_identity"
  count  = var.enable_user_assigned_identity ? 1 : 0

  name_prefix         = var.resource_name_prefix
  resource_group_name = var.target_resource_group_name
  location            = var.target_location
  tags                = var.common_tags

  depends_on = [terraform_data.live_scope_guard]
}

module "key_vault" {
  source = "../modules/key_vault"
  count  = var.enable_key_vault ? 1 : 0

  name_prefix           = var.resource_name_prefix
  resource_group_name   = var.target_resource_group_name
  location              = var.target_location
  tenant_id             = var.target_tenant_id
  subnet_id             = try(module.network[0].private_endpoint_subnet_id, "")
  virtual_network_id    = try(module.network[0].virtual_network_id, "")
  identity_principal_id = try(module.user_assigned_identity[0].principal_id, "")
  tags                  = var.common_tags

  depends_on = [terraform_data.live_scope_guard]
}

module "storage" {
  source = "../modules/storage"
  count  = var.enable_storage ? 1 : 0

  name_prefix          = var.resource_name_prefix
  storage_account_name = var.storage_account_name
  resource_group_name  = var.target_resource_group_name
  location             = var.target_location
  subnet_id            = try(module.network[0].private_endpoint_subnet_id, "")
  virtual_network_id   = try(module.network[0].virtual_network_id, "")
  tags                 = var.common_tags

  depends_on = [terraform_data.live_scope_guard]
}

module "monitoring" {
  source = "../modules/monitoring"
  count  = var.enable_monitoring ? 1 : 0

  name_prefix         = var.resource_name_prefix
  resource_group_name = var.target_resource_group_name
  location            = var.target_location
  tags                = var.common_tags

  depends_on = [terraform_data.live_scope_guard]
}

resource "azurerm_recovery_services_vault" "this" {
  count = var.enable_recovery_vault ? 1 : 0

  name                = "${var.resource_name_prefix}-rsv"
  resource_group_name = var.target_resource_group_name
  location            = var.target_location
  sku                 = "Standard"

  storage_mode_type             = "LocallyRedundant"
  cross_region_restore_enabled  = false
  public_network_access_enabled = false
  immutability                  = "Unlocked"
  tags                          = var.common_tags

  depends_on = [terraform_data.live_scope_guard]
}

resource "azurerm_role_assignment" "aks_registry_pull" {
  count = var.enable_aks && var.enable_container_registry ? 1 : 0

  scope                = try(module.container_registry[0].id, "")
  role_definition_name = "AcrPull"
  principal_id         = try(module.user_assigned_identity[0].principal_id, "")
  principal_type       = "ServicePrincipal"

  depends_on = [terraform_data.live_scope_guard]
}

resource "azapi_resource" "audit_policy_assignment" {
  count = var.enable_audit_policy_assignment ? 1 : 0

  type      = "Microsoft.Authorization/policyAssignments@2022-06-01"
  name      = "${var.resource_name_prefix}-audit"
  parent_id = "/subscriptions/${var.target_subscription_id}/resourceGroups/${var.target_resource_group_name}"
  body = {
    properties = {
      policyDefinitionId = var.policy_definition_id
      enforcementMode    = "DoNotEnforce"
    }
  }
  response_export_values = ["properties.enforcementMode", "properties.policyDefinitionId"]

  depends_on = [terraform_data.live_scope_guard]
}
