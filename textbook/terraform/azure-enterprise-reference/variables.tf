variable "use_workload_identity" {
  description = "Opt into Azure DevOps/Entra OIDC only for a separately approved protected pipeline run."
  type        = bool
  default     = false
}

variable "target_subscription_id" {
  description = "Exact target subscription ID. Empty until a separately authorized live run is prepared."
  type        = string
  default     = ""

  validation {
    condition     = var.target_subscription_id == "" || can(regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", var.target_subscription_id))
    error_message = "target_subscription_id must be empty or a UUID."
  }
}

variable "target_resource_group_name" {
  description = "Existing, explicitly approved resource group. This configuration never creates a resource group."
  type        = string
  default     = ""

  validation {
    condition     = var.target_resource_group_name == "" || can(regex("^rg-azure-cloudops-[a-z0-9-]{1,40}$", var.target_resource_group_name))
    error_message = "Use an explicitly scoped rg-azure-cloudops-* resource group name."
  }
}

variable "target_location" {
  description = "Azure region for resources, required only for an explicitly enabled plan."
  type        = string
  default     = ""
}

variable "allowed_subscription_ids" {
  description = "Exact subscription allowlist for the deployment batch; empty by default."
  type        = set(string)
  default     = []
}

variable "allowed_resource_group_names" {
  description = "Exact existing resource-group allowlist, including AKS node RG if AKS is enabled."
  type        = set(string)
  default     = []
}

variable "target_tenant_id" {
  description = "Tenant ID used by the Key Vault resource. Set only for an authorized, reviewed plan."
  type        = string
  default     = ""
}

variable "resource_name_prefix" {
  description = "Short lowercase prefix used to construct names within the approved scope."
  type        = string
  default     = ""

  validation {
    condition     = var.resource_name_prefix == "" || can(regex("^[a-z0-9][a-z0-9-]{1,18}[a-z0-9]$", var.resource_name_prefix))
    error_message = "resource_name_prefix must contain 3-20 lowercase letters, digits, or interior hyphens."
  }
}

variable "storage_account_name" {
  description = "Globally unique storage account name (3-24 lowercase letters or digits). Required only when storage is enabled."
  type        = string
  default     = ""

  validation {
    condition     = var.storage_account_name == "" || can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "storage_account_name must contain 3-24 lowercase letters or digits."
  }
}

variable "ssh_admin_username" {
  description = "Non-root Linux administrator name for the optional private VM."
  type        = string
  default     = "cloudopsadmin"

  validation {
    condition     = can(regex("^[a-z_][a-z0-9_-]{0,31}$", var.ssh_admin_username))
    error_message = "ssh_admin_username must be a valid Linux account name."
  }
}

variable "ssh_public_key" {
  description = "Public SSH key only; no private key is accepted or stored by this configuration."
  type        = string
  default     = ""

  validation {
    condition     = var.ssh_public_key == "" || can(regex("^ssh-(ed25519|rsa) ", var.ssh_public_key))
    error_message = "ssh_public_key must be empty or an ssh-ed25519/ssh-rsa public key."
  }
}

variable "common_tags" {
  description = "Tags applied to created resources. Add owner and cost-center values for a live scope."
  type        = map(string)
  default = {
    project    = "azure-cloudops"
    managed_by = "terraform"
  }
}

variable "enable_networking" {
  description = "Create the virtual network and isolated workload, AKS, and private-endpoint subnets."
  type        = bool
  default     = false
}

variable "enable_linux_vm" {
  description = "Create an SSH-key-only Linux VM with no public IP."
  type        = bool
  default     = false
}

variable "enable_aks" {
  description = "Create a private AKS cluster. Its generated node resource group must be separately allowlisted."
  type        = bool
  default     = false
}

variable "aks_node_resource_group_name" {
  description = "Explicit, new AKS node resource-group name in the allowlist; Azure creates it as a side effect."
  type        = string
  default     = ""
}

variable "enable_container_registry" {
  description = "Create a Premium, private-only Azure Container Registry and private endpoint."
  type        = bool
  default     = false
}

variable "enable_user_assigned_identity" {
  description = "Create a user-assigned managed identity."
  type        = bool
  default     = false
}

variable "enable_key_vault" {
  description = "Create a RBAC-enabled private Key Vault and grant the managed identity Secrets User at vault scope."
  type        = bool
  default     = false
}

variable "enable_storage" {
  description = "Create an OAuth-only private Storage account with Blob recovery settings and a private endpoint."
  type        = bool
  default     = false
}

variable "enable_monitoring" {
  description = "Create a pay-as-you-go Log Analytics workspace with explicit retention and daily quota."
  type        = bool
  default     = false
}

variable "enable_recovery_vault" {
  description = "Create a locally redundant Recovery Services vault. Backup items and policies are not created."
  type        = bool
  default     = false
}

variable "enable_audit_policy_assignment" {
  description = "Create an AzAPI policy assignment in DoNotEnforce mode at the target resource-group scope."
  type        = bool
  default     = false
}

variable "policy_definition_id" {
  description = "Full existing Azure Policy definition resource ID used only by the optional AzAPI assignment."
  type        = string
  default     = ""
}

variable "live_changes_authorized" {
  description = "Explicit assertion that the owner approved this exact deployment batch. False by default."
  type        = bool
  default     = false
}

variable "authorization_reference" {
  description = "Human-auditable owner approval/change reference; this string is not itself proof of authorization."
  type        = string
  default     = ""
}

variable "cost_estimate_verified" {
  description = "True only after current region/SKU pricing, dependencies, runtime, and cleanup are documented."
  type        = bool
  default     = false
}

variable "estimated_gross_batch_usd" {
  description = "Conservative gross estimate for the complete batch including dependencies and cleanup. Must be > 0."
  type        = number
  default     = 0

  validation {
    condition     = var.estimated_gross_batch_usd >= 0 && var.estimated_gross_batch_usd <= 0.70
    error_message = "The planned gross batch estimate must be between USD 0 and the USD 0.70 planning threshold."
  }
}

variable "cumulative_gross_estimate_before_usd" {
  description = "Previously committed project gross estimate, excluding credits or discounts."
  type        = number
  default     = 0

  validation {
    condition     = var.cumulative_gross_estimate_before_usd >= 0 && var.cumulative_gross_estimate_before_usd <= 1
    error_message = "Cumulative gross estimate must be between USD 0 and USD 1.00."
  }
}

variable "planned_runtime_minutes" {
  description = "Maximum planned runtime for this batch, bounded locally to one hour."
  type        = number
  default     = 0

  validation {
    condition     = var.planned_runtime_minutes >= 0 && var.planned_runtime_minutes <= 60
    error_message = "planned_runtime_minutes must be between 0 and 60."
  }
}
