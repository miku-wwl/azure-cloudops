# Read-only operational diagnostics

`../diagnostic_catalog.json` is the machine-readable catalog for the thirteen E6 diagnostic categories. It distinguishes a prepared command from an executed observation. All Azure examples require a resource ID and/or subscription supplied by the operator; they do not silently use `az account set` or change an Azure object.

## Local probes

- `python textbook/tools/network_probe.py tcp-tls --host <host> --port <port> [--tls] --timeout 5` resolves the explicit host and tests direct TCP/TLS within an overall probe deadline. TLS uses the operating system's certificate verification. By default, resolved IPs are replaced with SHA-256 references.
- `python textbook/tools/network_probe.py http-head --url <https-health-endpoint> --timeout 10` resolves then connects directly to one of the returned addresses, sends one HEAD request, does not use proxies or follow redirects, reads no body, and supplies no authorization header. Use only a designated health endpoint that permits unauthenticated HEAD.
- `python textbook/tools/token_audience.py --expected-audience <audience>` prompts without echo in an interactive terminal and prints an allowlist of claims. It does not validate signatures or acquire tokens. Never paste a token into command arguments, source, terminal recording, or a shared log.

The probes report only what they observe. The configured timeout bounds how long the CLI waits for DNS, but Python cannot cancel an OS `getaddrinfo` call; a timed-out lookup runs in a daemon thread until the resolver returns. DNS resolution does not prove a TCP path, TLS verification does not prove application health, and HTTP HEAD status does not prove a business request works.

## Azure and Kubernetes observations

The catalog gives the minimum read command and the distinguishing evidence for routes, effective NSG, Private Endpoint/DNS, identity, RBAC, Key Vault, Policy, Kubernetes image pulls, and Azure Monitor metrics. Before use, substitute only values from the approved scope, record operator/tenant/subscription/run time, and confirm the operator has the needed read permissions. A permission error and an empty result remain distinct outcomes.

Commands are examples, not evidence. Resource Graph inventory is implemented separately in `../azure_inventory.py`; it pages by the returned continuation token, bounds requests, uses an explicit subscription every time, reports incomplete pages, redacts identifiers by default, and never queries resource properties or tags.

## Verification status

- JSON structure and all thirteen category IDs are covered by local tests.
- Network probe verification uses loopback-only temporary listeners. No external host was contacted.
- The token reader uses synthetic JWTs only. No token was acquired or read.
- No Azure CLI command, Kubernetes command, Azure resource/API query, metric query, KQL query, or billing query was executed for E6.
- For cloud behavior and current field requirements, consult the primary references listed in `textbook/SOURCE_MAP.md` and each query's schema notes.
