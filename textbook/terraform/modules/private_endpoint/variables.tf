variable "name_prefix" {
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

variable "target_resource_id" {
  type = string
}

variable "subresource_name" {
  type = string
}

variable "private_dns_zone_name" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
