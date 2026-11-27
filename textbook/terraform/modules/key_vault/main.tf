resource "azurerm_key_vault" "this" {
  name                          = "${var.name_prefix}-kv"
  resource_group_name           = var.resource_group_name
  location                      = var.location
  tenant_id                     = var.tenant_id
  sku_name                      = "standard"
  rbac_authorization_enabled    = true
  soft_delete_retention_days    = 90
  purge_protection_enabled      = true
  public_network_access_enabled = false

  network_acls {
    bypass         = "None"
    default_action = "Deny"
  }

  tags = var.tags
}

resource "azurerm_role_assignment" "secrets_reader" {
  scope                = azurerm_key_vault.this.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = var.identity_principal_id
  principal_type       = "ServicePrincipal"
}

module "private_endpoint" {
  source = "../private_endpoint"

  name_prefix           = "${var.name_prefix}-kv"
  resource_group_name   = var.resource_group_name
  location              = var.location
  subnet_id             = var.subnet_id
  virtual_network_id    = var.virtual_network_id
  target_resource_id    = azurerm_key_vault.this.id
  subresource_name      = "vault"
  private_dns_zone_name = "privatelink.vaultcore.azure.net"
  tags                  = var.tags
}
