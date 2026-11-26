terraform {
  required_version = ">= 1.7.0"
}

variable "environment" {
  type    = string
  default = "dev"

  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "environment must be dev, test, or prod."
  }
}

variable "scope" {
  type    = string
  default = "lab/offline/rg-training"

  validation {
    condition     = startswith(var.scope, "lab/")
    error_message = "This local-only contract accepts lab/ scopes."
  }
}

module "workload" {
  source      = "./modules/workload"
  environment = var.environment
  scope       = var.scope
}

output "resource_contract" {
  value = module.workload.resource_contract
}

output "release_contract" {
  value = module.workload.release_contract
}
