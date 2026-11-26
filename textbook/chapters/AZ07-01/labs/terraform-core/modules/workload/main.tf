variable "environment" {
  type = string
}

variable "scope" {
  type = string
}

resource "terraform_data" "scope_contract" {
  input = {
    environment = var.environment
    scope       = var.scope
    provider    = "terraform_data (Terraform built-in)"
    cloud_api   = "none"
  }
}

resource "terraform_data" "release_contract" {
  input = {
    environment          = terraform_data.scope_contract.input.environment
    scope                = terraform_data.scope_contract.input.scope
    prerequisite_address = "terraform_data.scope_contract"
    status               = "plan-only local contract"
  }
}

output "resource_contract" {
  value = terraform_data.scope_contract.input
}

output "release_contract" {
  value = terraform_data.release_contract.input
}
