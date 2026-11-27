variable "name_prefix" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "node_resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "subnet_id" {
  type = string
}

variable "kubelet_identity_id" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
