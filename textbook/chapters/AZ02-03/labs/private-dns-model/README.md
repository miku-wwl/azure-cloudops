# Private DNS and Private Endpoint local model

From this directory, run:

```powershell
python -m unittest -v
python dns_model.py
```

The JSON fixture uses reserved documentation addresses and a fictional Storage Blob name. The model selects between a private A record, a public answer, or NXDOMAIN, then evaluates endpoint approval, public-network access and a separate data-authorization assertion. It makes no DNS packet, TLS handshake, network probe, Azure API call or resource change.

The model does not implement real DNS delegation or CNAME processing, resolver caches or TTLs, Azure Private DNS, Private Resolver, Storage firewalls, routes, NSGs, TLS, Entra ID, SAS, keys or Azure Storage authorization. `data_authorized` is an input assertion, not an RBAC evaluator. The public address is a documentation-only fixture, not a reachable endpoint.
