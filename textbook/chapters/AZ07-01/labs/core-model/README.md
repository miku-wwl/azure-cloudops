# Terraform Core reasoning model

This standard-library model makes small, deterministic checks for a teaching scenario:

- dependency-first graph ordering and cycle rejection;
- synthetic AzureRM/AzAPI provider selection;
- unique Terraform address to remote object bindings;
- simplified lifecycle action classification; and
- import proposal behavior and duplicate-binding rejection.

Run from the repository root:

    python -m unittest discover -s textbook/chapters/AZ07-01/labs/core-model -p "test_*.py" -v

This is not Terraform Core, a provider, an Azure API emulator, a plan parser, or a live-state tool. It does not authenticate, initialize cloud providers, contact ARM, perform an import, or prove Azure behavior. The separately provided terraform-core lab is executed by Terraform CLI with its built-in terraform_data resource and no cloud provider.
