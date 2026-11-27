variable "name_prefix" {
  type = string
}

variable "storage_account_name" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "subnet_id" {
  type = string
}

variable "virtual_network_id" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
