resource "azurerm_container_registry" "this" {
  name                          = replace(var.name_prefix, "-", "")
  resource_group_name           = var.resource_group_name
  location                      = var.location
  sku                           = "Premium"
  admin_enabled                 = false
  anonymous_pull_enabled        = false
  public_network_access_enabled = false
  network_rule_bypass_option    = "None"
  data_endpoint_enabled         = false
  export_policy_enabled         = false

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

module "private_endpoint" {
  source = "../private_endpoint"

  name_prefix           = "${var.name_prefix}-acr"
  resource_group_name   = var.resource_group_name
  location              = var.location
  subnet_id             = var.subnet_id
  virtual_network_id    = var.virtual_network_id
  target_resource_id    = azurerm_container_registry.this.id
  subresource_name      = "registry"
  private_dns_zone_name = "privatelink.azurecr.io"
  tags                  = var.tags
}
