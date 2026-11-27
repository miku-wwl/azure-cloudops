terraform {
  required_version = ">= 1.7.0, < 2.0.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 5.15.0"
    }
    azapi = {
      source  = "Azure/azapi"
      version = "= 2.14.0"
    }
  }
}

provider "azurerm" {
  subscription_id                 = var.target_subscription_id
  use_cli                         = false
  use_msi                         = false
  use_oidc                        = false
  use_aks_workload_identity       = false
  resource_provider_registrations = "none"

  features {}
}

provider "azapi" {
  subscription_id            = var.target_subscription_id
  use_cli                    = false
  use_msi                    = false
  use_oidc                   = false
  skip_provider_registration = true
}
