# Copy this file to a protected, ignored backend.<environment>.hcl outside Git.
# Replace every example value before an explicitly approved remote-state run.
resource_group_name  = "REPLACE_WITH_EXISTING_STATE_RESOURCE_GROUP"
storage_account_name = "replacewithstateaccount"
container_name       = "tfstate"
key                  = "platform/dev.tfstate"
