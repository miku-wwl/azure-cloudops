terraform {
  required_version = ">= 1.7.0, < 2.0.0"

  # Empty-by-default remote backend. Live use requires an external protected
  # .tfbackend file and a separately authorized AzureRM OIDC session.
  backend "azurerm" {
    use_oidc             = true
    use_azuread_auth     = true
    use_cli              = false
    use_msi              = false
    lookup_blob_endpoint = false
  }

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
  use_oidc                        = var.use_workload_identity
  use_aks_workload_identity       = false
  resource_provider_registrations = "none"

  features {}
}

provider "azapi" {
  subscription_id            = var.target_subscription_id
  use_cli                    = false
  use_msi                    = false
  use_oidc                   = var.use_workload_identity
  skip_provider_registration = true
}
