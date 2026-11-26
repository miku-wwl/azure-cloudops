run "marker_content_is_declared" {
  command = plan

  assert {
    condition     = local_file.marker.content == var.desired_content
    error_message = "The managed local marker must match the declared input."
  }
}

run "lock_holder_is_absent_by_default" {
  command = plan

  assert {
    condition     = length(terraform_data.lock_holder) == 0
    error_message = "The interactive lock gate must remain opt-in."
  }
}