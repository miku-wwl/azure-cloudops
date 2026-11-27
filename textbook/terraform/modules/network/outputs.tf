output "virtual_network_id" {
  value = azurerm_virtual_network.this.id
}

output "workload_subnet_id" {
  value = azurerm_subnet.workload.id
}

output "aks_subnet_id" {
  value = azurerm_subnet.aks.id
}

output "private_endpoint_subnet_id" {
  value = azurerm_subnet.private_endpoints.id
}
