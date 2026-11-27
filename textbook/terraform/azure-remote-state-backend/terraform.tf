terraform {
  required_version = ">= 1.10.0, < 2.0.0"

  backend "azurerm" {
    use_oidc             = true
    use_azuread_auth     = true
    use_cli              = false
    use_msi              = false
    lookup_blob_endpoint = false
  }
}
