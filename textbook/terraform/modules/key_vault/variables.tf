variable "name_prefix" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "tenant_id" {
  type = string
}

variable "subnet_id" {
  type = string
}

variable "virtual_network_id" {
  type = string
}

variable "identity_principal_id" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
