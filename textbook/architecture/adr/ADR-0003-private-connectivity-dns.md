# ADR-0003 — Private connectivity and DNS

- Status: Accepted as the reference pattern; no private endpoint or DNS link deployed.
- Date: 2026-11-27.
- Context: private service connectivity depends on network paths, DNS answers, endpoint lifecycle, service network policy and data-plane authorization.

## Decision

For a service that supports Private Link, create an endpoint in the owning workload network, attach the service-appropriate private DNS zone through a zone group when supported, and link zones to only the VNets that need to resolve them. Define ownership for central zones, links, forwarding/resolver rules and stale-record cleanup. Keep `name resolution`, `network reachability`, `service firewall`, `TLS`, `identity` and `data permissions` as separate acceptance checks.

Do not add Azure DNS Private Resolver to the lab by default. Use it only when a hybrid/custom-DNS requirement needs managed forwarding and the current cost and deployment requirements have been reviewed. For a small conditional experiment, an external runner must already have an approved path to the VNet; do not add a VM or VPN silently.

## Consequences

- Private DNS links and zone groups reduce manual record drift but require shared-zone change ownership.
- A public CNAME, private IP answer or successful TCP handshake is not proof of authorized data access.
- Private Endpoint, service, DNS and network dependencies may each have separate costs and teardown behavior.
- If the scenario lacks an approved private network execution context, it remains documentation/local-only.

## Source

- [Private Endpoint DNS configuration](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-dns)
- [Troubleshoot Private Endpoint DNS](https://learn.microsoft.com/en-us/troubleshoot/azure/private-link/troubleshoot-private-endpoint-dns-resolution)
- [Troubleshoot NXDOMAIN from Private DNS](https://learn.microsoft.com/en-us/troubleshoot/azure/dns/troubleshoot-private-dns-zone-override-nxdomain)
