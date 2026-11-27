output "enabled_service_categories" {
  description = "Azure service categories explicitly enabled for this plan; empty by default."
  value       = local.enabled_categories
}

output "azure_resources_enabled" {
  description = "Whether any Azure resource feature is enabled. This is a plan indicator, not authorization evidence."
  value       = local.any_azure_feature_enabled
}

output "virtual_network_id" {
  description = "Virtual network ID for the planned network, when networking is enabled directly or as a dependency."
  value       = try(module.network[0].virtual_network_id, null)
}

output "workload_subnet_id" {
  description = "Subnet ID for private VM workloads, when networking is enabled."
  value       = try(module.network[0].workload_subnet_id, null)
}

output "aks_subnet_id" {
  description = "Dedicated subnet ID for AKS nodes, when networking is enabled."
  value       = try(module.network[0].aks_subnet_id, null)
}

output "private_endpoint_subnet_id" {
  description = "Dedicated subnet ID used by private service endpoints."
  value       = try(module.network[0].private_endpoint_subnet_id, null)
}

output "linux_vm_private_ip" {
  description = "Private address assigned to the optional SSH-key-only VM. No public IP is created."
  value       = try(module.linux_vm[0].private_ip_address, null)
}

output "container_registry_login_server" {
  description = "Private registry login endpoint, when ACR is enabled."
  value       = try(module.container_registry[0].login_server, null)
}

output "storage_account_id" {
  description = "Storage account ID, when the private OAuth-only storage module is enabled."
  value       = try(module.storage[0].storage_account_id, null)
}

output "log_analytics_workspace_id" {
  description = "Workspace resource ID, when monitoring is enabled."
  value       = try(module.monitoring[0].id, null)
}

output "recovery_services_vault_id" {
  description = "Recovery Services vault ID; no backup policy or protected item is created."
  value       = try(azurerm_recovery_services_vault.this[0].id, null)
}
