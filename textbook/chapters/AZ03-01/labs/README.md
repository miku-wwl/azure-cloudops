# AZ03-01 offline authorization lab

Run from this directory:

~~~powershell
cd textbook/chapters/AZ03-01/labs/authorization-model
python -m unittest -v
python authorization_model.py
~~~

The fixture is deliberately synthetic. It checks a caller-supplied trust assertion, issuer, tenant, audience, not-before and expiry values, then evaluates the fixture's direct principal assignments, parent-scope inheritance, role Actions/DataActions and the role-local NotActions/NotDataActions subtraction. Tokens, tenant IDs, scopes, identities and operations are fictional test data; no access token is acquired or printed.

The model does not parse JWTs, verify signatures or signing keys, fetch metadata, perform OAuth, model token-version claim variations, resolve groups, inspect real role definitions or assignments, or reproduce Azure RBAC. It omits deny assignments, role-assignment conditions, PIM activation, propagation delays, service-specific authorization modes, Storage keys/SAS and provider-specific evaluation details. It does not call Azure, Microsoft Graph or any network endpoint.

The requests intentionally distinguish an ARM-audience token from the Storage audience expected by a data API, a control-plane Reader from a blob DataAction, a child scope from its sibling, and a role-local exclusion from a deny assignment. The model reports only its synthetic decision and matching fixture assignment IDs.
