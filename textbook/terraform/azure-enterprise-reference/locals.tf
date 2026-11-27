locals {
  azure_features = {
    networking             = var.enable_networking
    linux_vm               = var.enable_linux_vm
    aks                    = var.enable_aks
    container_registry     = var.enable_container_registry
    user_assigned_identity = var.enable_user_assigned_identity
    key_vault              = var.enable_key_vault
    storage                = var.enable_storage
    monitoring             = var.enable_monitoring
    recovery_vault         = var.enable_recovery_vault
    audit_policy           = var.enable_audit_policy_assignment
  }

  any_azure_feature_enabled = anytrue(values(local.azure_features))
  enabled_categories        = [for name, enabled in local.azure_features : name if enabled]
  network_required          = var.enable_networking || var.enable_linux_vm || var.enable_aks || var.enable_container_registry || var.enable_key_vault || var.enable_storage

  target_rg_is_allowlisted = contains(var.allowed_resource_group_names, var.target_resource_group_name)
  subscription_is_allowlisted = contains(
    var.allowed_subscription_ids,
    lower(var.target_subscription_id)
  ) || contains(var.allowed_subscription_ids, var.target_subscription_id)
}
