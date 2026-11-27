resource "azurerm_storage_account" "this" {
  name                     = var.storage_account_name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_kind             = "StorageV2"
  account_tier             = "Standard"
  account_replication_type = "LRS"

  https_traffic_only_enabled      = true
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = false
  default_to_oauth_authentication = true
  public_network_access           = "Disabled"
  local_user_enabled              = false

  blob_properties {
    versioning_enabled  = true
    change_feed_enabled = true

    delete_retention_policy {
      days = 7
    }

    container_delete_retention_policy {
      days = 7
    }
  }

  tags = var.tags
}

module "private_endpoint" {
  source = "../private_endpoint"

  name_prefix           = "${var.name_prefix}-blob"
  resource_group_name   = var.resource_group_name
  location              = var.location
  subnet_id             = var.subnet_id
  virtual_network_id    = var.virtual_network_id
  target_resource_id    = azurerm_storage_account.this.id
  subresource_name      = "blob"
  private_dns_zone_name = "privatelink.blob.core.windows.net"
  tags                  = var.tags
}
