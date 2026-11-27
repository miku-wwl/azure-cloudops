resource "azurerm_log_analytics_workspace" "this" {
  name                = "${var.name_prefix}-law"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
  daily_quota_gb      = 1

  internet_ingestion_access_type = "Enabled"
  internet_query_access_type     = "Enabled"
  local_authentication_enabled   = false

  tags = var.tags
}
