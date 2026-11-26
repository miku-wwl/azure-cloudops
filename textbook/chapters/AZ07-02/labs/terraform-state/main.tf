terraform {
  required_version = ">= 1.10.0"

  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.9.1"
    }
  }
}

variable "desired_content" {
  description = "Desired text written to the disposable local lab file."
  type        = string
  default     = "managed=terraform\n"
}

variable "hold_lock" {
  description = "Add a local provisioner that pauses for interactive lock-contention practice."
  type        = bool
  default     = false
}

resource "local_file" "marker" {
  filename        = "${path.module}/work/managed-marker.txt"
  content         = var.desired_content
  file_permission = "0600"
}

resource "terraform_data" "lock_holder" {
  count = var.hold_lock ? 1 : 0

  input = "The local provisioner is holding this Terraform operation open."

  provisioner "local-exec" {
    command     = "python scripts/hold_state_lock.py"
    working_dir = path.module
  }
}