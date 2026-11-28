# AZ00-01 labs

## scope-model

Run from textbook/chapters/AZ00-01/labs/scope-model:

    python -m unittest -v
    python scope_model.py

This pure-Python teaching fixture demonstrates ancestry-based role assignment scope and keeps Actions separate from DataActions. All principal names, subscription identifiers and resource names are synthetic. It does not call Azure, authenticate, change a subscription or model the full Azure RBAC decision engine. Its exclusions are stated in the chapter.

This exercise uses synthetic local data and has not been run against an Azure subscription. It does not authenticate, change the active subscription, or register a Provider.
