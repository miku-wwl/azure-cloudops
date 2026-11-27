# Conditional Azure Storage backend

This is a real Terraform `azurerm` backend configuration for a later, explicitly authorized Stage 3 run. It is separate from the offline AZ07-02 lab and the E3 mock-test root. The backend selects a Blob by storage account, container, and key; it uses Entra ID with workload identity federation, disables Azure CLI and managed-identity fallback, and leaves credentials out of HCL.

The sample backend values are placeholders. Copy `backend.example.hcl` to a protected file outside the checkout, replace the existing Storage Account/container/key, and pass that file to `terraform init -backend-config=<path>`. Supply tenant/client identifiers and Azure DevOps OIDC endpoint values through the protected workload-identity Service Connection environment. Never put a secret, access key, SAS token, or token in the backend file or command history. Do not set `lookup_blob_endpoint=true` unless the storage account requires endpoint discovery and the identity has the additional management-plane Reader permission.

The storage account and private container must already exist before Terraform initializes this backend. Bootstrap those separately; this configuration does not create them. Scope the state-writing identity to the existing state container with `Storage Blob Data Contributor`. Azure Blob locking then applies to one Blob key. Separate keys do not prevent two roots from declaring the same Azure object.

`terraform init` against this directory is intentionally **NOT_RUN**. Initializing it would make a real Azure Storage data-plane request and can read or create remote State. Stage 2 performs no Azure request. Before any Stage 3 use, verify the exact organization, tenant, subscription, resource group, account, container, key, role scope, backup and the explicit approval for that experiment.

Sources: [HashiCorp AzureRM backend](https://developer.hashicorp.com/terraform/language/backend/azurerm), [HashiCorp backend configuration](https://developer.hashicorp.com/terraform/language/backend), and [Microsoft Learn Terraform state in Azure Storage](https://learn.microsoft.com/en-us/azure/developer/terraform/store-state-in-azure-storage).
