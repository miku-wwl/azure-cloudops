# AZ00-01 labs

## scope-model

Run from textbook/chapters/AZ00-01/labs/scope-model:

    python -m unittest -v
    python scope_model.py

This pure-Python teaching fixture demonstrates ancestry-based role assignment scope and keeps Actions separate from DataActions. All principal names, subscription identifiers and resource names are synthetic. It does not call Azure, authenticate, change a subscription or model the full Azure RBAC decision engine. Its exclusions are stated in the chapter.

Cloud status: LIVE_NOT_RUN. Local status is updated only from actual test output recorded in textbook/PROGRESS.md.
