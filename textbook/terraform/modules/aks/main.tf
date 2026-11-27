resource "azurerm_kubernetes_cluster" "this" {
  name                = "${var.name_prefix}-aks"
  location            = var.location
  resource_group_name = var.resource_group_name
  node_resource_group = var.node_resource_group_name
  dns_prefix          = "${var.name_prefix}-aks"

  private_cluster_enabled   = true
  private_dns_zone_id       = "System"
  local_account_disabled    = true
  run_command_enabled       = false
  oidc_issuer_enabled       = true
  workload_identity_enabled = true
  sku_tier                  = "Free"

  node_provisioning_profile {
    mode               = "Manual"
    default_node_pools = "None"
  }

  default_node_pool {
    name                        = "system"
    vm_size                     = "Standard_B2s"
    vnet_subnet_id              = var.subnet_id
    auto_scaling_enabled        = true
    min_count                   = 1
    max_count                   = 2
    node_count                  = 1
    temporary_name_for_rotation = "systemtmp"
    os_sku                      = "Ubuntu"
  }

  identity {
    type = "SystemAssigned"
  }

  kubelet_identity {
    user_assigned_identity_id = var.kubelet_identity_id
  }

  network_profile {
    network_plugin    = "azure"
    network_policy    = "azure"
    load_balancer_sku = "standard"
    outbound_type     = "loadBalancer"
    service_cidr      = "10.241.0.0/16"
    dns_service_ip    = "10.241.0.10"
  }

  tags = var.tags
}
