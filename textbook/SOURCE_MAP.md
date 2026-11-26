# Source-to-section map

Research date for AZ00-01: 2026-11-26. Azure claims are based on Microsoft Learn primary documentation. The local scope program is a deliberately limited fixture, not a cloud emulator.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ00-01 §01, Fig 1-1 | Platform and workload landing zones are distinct parts of a multi-subscription architecture; management-group hierarchy carries policy | Cloud Adoption Framework: landing zones and management groups; subscription design area | SOURCE-ANALYSED; architecture guidance, not one mandatory organization chart |
| AZ00-01 §01 | Subscription is a management, billing and scale boundary; workload environment placement depends on organizational requirements | CAF subscription considerations | SOURCE-ANALYSED; exact subscription count is workload and ownership dependent |
| AZ00-01 §02, Fig 1-2 | ARM is a consistent management layer; control-plane operations are distinct from resource data-plane endpoints | ARM overview; control plane and data plane operations | SOURCE-ANALYSED; resource-provider and service-specific details vary |
| AZ00-01 §02, Fig 1-2 | A 202 response can require status polling using operation headers and Retry-After | ARM asynchronous operations | SOURCE-ANALYSED; exact headers and status endpoint depend on operation |
| AZ00-01 §03, Fig 1-3 | Provider registration is subscription-scoped, can be asynchronous/per-region, requires register/action, and does not replace API-version/location support | Resource providers and types; registration errors | SOURCE-ANALYSED; verify actual resource type and region before a live deployment |
| AZ00-01 §03 | Azure may automatically register providers for some Portal/ARM/Bicep operations; only register needed providers | Resource providers and types | SOURCE-ANALYSED |
| AZ00-01 §05–06 | Ancestor role assignments reach descendant scopes in the fixture; control and data operations use separate grant lists | scope_model.py and test_scope_model.py | VERIFIED locally 2026-11-26, seven unittest cases; fixture behavior only, not Azure authorization |
| AZ00-01 §06 | Azure authorization or resource-provider behavior was not queried | No Azure request was run | NOT_RUN |

## Primary references

- https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview
- https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/control-plane-and-data-plane
- https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-providers-and-types
- https://learn.microsoft.com/en-us/azure/azure-resource-manager/troubleshooting/error-register-resource-provider
- https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/async-operations
- https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/
- https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/design-area/resource-org-management-groups
- https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/design-area/resource-org-subscriptions
- https://learn.microsoft.com/en-us/azure/role-based-access-control/scope-overview
- https://learn.microsoft.com/en-us/azure/governance/policy/concepts/scope

## AZ01-01 — Well-Architected reliability

Research date: 2026-11-26. This chapter distinguishes official service guidance, a fictional workload target and the deterministic local fixture. Availability SKU/region claims must be rechecked for the actual service at deployment time.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ01-01 §01, Fig 2-1 | Reliability begins with critical flows, failure-mode analysis, targets, redundancy, testing and health measurement | WAF reliability principles and design-review checklist | SOURCE-ANALYSED; the framework is guidance, not proof of a particular workload's availability |
| AZ01-01 §02, Fig 2-1 | Availability Set FD/UD separate some VM hardware and maintenance events; sets don't cover app/OS faults or all datacenter-wide events | Availability sets overview; VM reliability guide | SOURCE-ANALYSED; exact SLA conditions and placement must be checked against current VM terms |
| AZ01-01 §02, Fig 2-1 / §03, Fig 2-2 | A zonal VM/resource isn't automatically resilient; zone-redundant behavior and customer/platform failover responsibility vary by service, SKU, region and configuration | Availability zones overview; zonal resource resiliency; service reliability guides | SOURCE-ANALYSED; do not infer the behavior of a named SKU from a region-level support list |
| AZ01-01 §02–03 | Zone redundancy doesn't protect a full-region outage; multi-region recovery requires workload-specific RTO/RPO, data residency and operational planning | WAF regions and availability zones; DR planning | SOURCE-ANALYSED; the chapter doesn't promise a universal region-pair or recovery time |
| AZ01-01 §04 / Fig 2-3 | User-facing SLI/SLO, error budget, supplier SLA, RTO and RPO are separate concepts; percentage-to-minutes conversion only fits time-based availability | WAF reliability metrics; reliability testing; SLA interpretation | SOURCE-ANALYSED; 99.95% and 30-day examples are fictional assumptions, not Azure commitments |
| AZ01-01 §06 | AND/OR path evaluation, serial/parallel formulae and synthetic fault matrix | `labs/reliability-model/reliability_model.py`, fixture and tests | LOCAL_VERIFIED 2026-11-26; deterministic, no probabilities in scenario matrix and no Azure behavior modeled |
| AZ01-01 §07–08 | A healthy VM/API endpoint alone does not prove a payment flow, data integrity, RTO or RPO | WAF reliability testing; synthetic acceptance exercises | DESIGN_GUIDANCE; no production or Azure DR drill was performed |

### Primary references

- https://learn.microsoft.com/en-us/azure/well-architected/reliability/principles
- https://learn.microsoft.com/en-us/azure/well-architected/resiliency/design-requirements
- https://learn.microsoft.com/en-us/azure/reliability/availability-zones-overview
- https://learn.microsoft.com/en-us/azure/reliability/availability-zones-service-support
- https://learn.microsoft.com/en-us/azure/reliability/availability-zones-zonal-resource-resiliency
- https://learn.microsoft.com/en-us/azure/virtual-machines/availability-set-overview
- https://learn.microsoft.com/en-us/azure/reliability/reliability-virtual-machines
- https://learn.microsoft.com/en-us/azure/well-architected/resiliency/regions-availability-zones
- https://learn.microsoft.com/en-us/azure/well-architected/design-guides/disaster-recovery
- https://learn.microsoft.com/en-us/azure/well-architected/reliability/metrics
- https://learn.microsoft.com/en-us/azure/reliability/concept-service-level-agreements
- https://learn.microsoft.com/en-us/azure/well-architected/resiliency/reliability-test
- https://learn.microsoft.com/en-us/azure/well-architected/reliability/tradeoffs

## AZ02-01 — VNet, UDR and effective routes

Research date: 2026-11-26. The chapter separates Microsoft-documented routing behavior from the intentionally narrow IPv4 fixture. The CLI commands are documented examples and were not run against Azure.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ02-01 §01, Fig 3-1 | A subnet can be associated with at most one route table; a route table can be associated with multiple subnets; a VM NIC's effective routes combine its associated route table, system routes and BGP-propagated routes | Manage route tables; view effective routes | SOURCE-ANALYSED; effective-route view is for VM NICs and does not prove end-to-end reachability |
| AZ02-01 §02, Fig 3-1 | Azure uses longest-prefix matching; routes with the same prefix use UDR > BGP > system | Virtual network traffic routing | SOURCE-ANALYSED; VNet, peering and service-endpoint routes have documented exceptions |
| AZ02-01 §02 | Service-endpoint next-hop routes cannot be overridden by a route table; some special system routes are preferred even over more-specific BGP routes | Virtual network traffic routing | SOURCE-ANALYSED; the local model refuses these special route kinds rather than approximating them |
| AZ02-01 §01–02 | A VirtualAppliance UDR needs a next-hop IP; the NVA NIC requires IP forwarding to forward third-party traffic | Virtual network traffic routing; route-table configuration | SOURCE-ANALYSED; does not prove appliance policy, forwarding or return route |
| AZ02-01 §02 | `VirtualApplianceEcmp` is documented as public preview and does not guarantee flow symmetry or synchronize NVA state | Equal-cost multipath routing for user-defined routes | SOURCE-ANALYSED as of research date; not enabled or tested |
| AZ02-01 §03, Fig 3-2 | Azure Virtual WAN dual-role active-active NVA ECMP can send directions to different instances; stateful inspection drops asymmetric routing unless the NVA supports it or shares state | Azure Virtual WAN routing policies | SOURCE-ANALYSED for the documented Virtual WAN topology; not generalized to all Azure routes |
| AZ02-01 §06, Fig 3-3 | Network Watcher Next Hop returns next-hop type, IP and route-table ID for one VM/source/destination query; UDR results identify the containing route table, otherwise `System Route` | Next Hop overview; Azure CLI command reference | SOURCE-ANALYSED; a selected hop does not prove connectivity, the return route or application success |
| AZ02-01 §07 | Prefix matching, source tie-break, subnet associations, selected NVA and modeled forward/return symmetry | `labs/route-model/route_model.py`, JSON fixture and 13 tests | LOCAL_VERIFIED 2026-11-26 on Windows Python 3.13.9 and WSL; synthetic narrow model, no Azure API or data plane |

### Primary references

- https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview
- https://learn.microsoft.com/en-us/azure/virtual-network/manage-route-table
- https://learn.microsoft.com/en-us/azure/network-watcher/next-hop-overview
- https://learn.microsoft.com/en-us/cli/azure/network/watcher?view=azure-cli-latest#az-network-watcher-show-next-hop
- https://learn.microsoft.com/en-us/azure/virtual-wan/how-to-routing-policies
- https://learn.microsoft.com/en-us/azure/architecture/networking/architecture/hub-spoke

## AZ02-02 — NSG, ASG and network diagnostics

Research date: 2026-11-26. Microsoft Learn page revisions observed during review: NSG overview 2025-07-15, ASG overview 2025-07-25, IP Flow Verify 2025-09-23, traffic-filter troubleshooting 2026-10-08, and Connection Troubleshoot 2026-11-17. CLI states are the current official reference states on the research date.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ02-02 §01, Fig 4-1 | Custom NSG priority range is 100–4096; lower number evaluates first; first match stops; Azure default inbound/outbound rules have priorities 65000–65500 | Network security groups overview | SOURCE-ANALYSED; default service-tag scope and effective rules must be checked for the actual NIC |
| AZ02-02 §02, Fig 4-2 | An NSG can be associated to subnet and/or NIC; inbound processing is subnet NSG then NIC NSG and both must allow; NIC effective rules aggregate rules from both scopes | Diagnose a virtual machine network traffic filter problem | SOURCE-ANALYSED; specific to documented inbound behavior; chapter does not invent outbound scope order |
| AZ02-02 §02 | ASG membership is assigned to NICs; NSG rules reference source/destination ASGs; NICs within a group and groups used together in one rule are constrained to the same VNet | Application Security Groups overview | SOURCE-ANALYSED; ASG is a network selector, not identity authorization |
| AZ02-02 §04, Fig 4-3 | NSGs are stateful; flow records allow response traffic; removing/changing a rule does not interrupt existing connections and rules affect new connections | Network security groups overview | SOURCE-ANALYSED; fixture's flow state is an intentionally simplified teaching representation |
| AZ02-02 §05 | `az network nic list-effective-nsg` shows NIC/subnet rules, requires a running VM and an associated NSG, and should be run per NIC; IP Flow Verify checks TCP/UDP rules plus AVNM admin rules | Traffic-filter troubleshooting; IP Flow Verify overview; Azure CLI reference | SOURCE-ANALYSED; neither effective rules nor IP Flow Verify proves connection or application success |
| AZ02-02 §05 | Connection Troubleshoot has an agentless test path and detects connectivity, NSG, route, DNS, guest firewall and listener issues; CLI `test-connectivity` remains Core Preview | Connection Troubleshoot overview; Azure CLI reference | SOURCE-ANALYSED; diagnostic tests actively probe endpoints; no live probe was executed |
| AZ02-02 §06 | Priority and first-match evaluation, ASG membership, subnet/NIC custom-rule decisions, and simplified established-flow behavior | `labs/nsg-model/nsg_model.py`, JSON fixture and 13 tests | LOCAL_VERIFIED 2026-11-26 on Windows Python 3.13.9 and WSL; custom-rule IPv4 TCP/UDP fixture, no Azure API or platform defaults |

### Primary references

- https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview
- https://learn.microsoft.com/en-us/azure/virtual-network/application-security-groups
- https://learn.microsoft.com/en-us/azure/virtual-network/diagnose-network-traffic-filter-problem
- https://learn.microsoft.com/en-us/azure/network-watcher/network-watcher-ip-flow-verify-overview
- https://learn.microsoft.com/en-us/azure/network-watcher/network-watcher-connectivity-overview
- https://learn.microsoft.com/en-us/cli/azure/network/nic?view=azure-cli-latest#az-network-nic-list-effective-nsg
- https://learn.microsoft.com/en-us/cli/azure/network/watcher?view=azure-cli-latest#az-network-watcher-test-ip-flow
- https://learn.microsoft.com/en-us/cli/azure/network/watcher?view=azure-cli-latest#az-network-watcher-test-connectivity

## AZ02-03 — Private DNS, Private Link and Private Endpoint

Research date: 2026-11-26. The chapter separates Microsoft-documented Storage/Private Link behavior, an explicitly labeled inference about TLS hostname validation, and a small local decision model. Azure CLI command syntax and the current `NxDomainRedirect` VNet-link policy were checked in official Microsoft Learn references. No Azure command or probe was executed.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ02-03 §01, Fig 5-1 | A PE is a NIC with private IP, target subresource and approval lifecycle; only Approved connections send traffic | Private endpoint overview | SOURCE-ANALYSED; no Azure PE was queried or created |
| AZ02-03 §02, Fig 5-1 | Storage Blob uses `privatelink.blob.core.windows.net`; original service FQDN remains the connection URL; DNS CNAME/A answers vary by resolver context | Storage private endpoints; PE DNS zone values | SOURCE-ANALYSED; TLS/SNI implication is explicitly marked as inference from the original-host requirement |
| AZ02-03 §02 | Public CNAME visibility proves a global name exists, not PE attachment, private address or data access; a linked zone missing an A record can return NXDOMAIN; `NxDomainRedirect` falls back on NXDOMAIN | PE DNS zone values; CLI private DNS link vnet reference | SOURCE-ANALYSED; fixture models only the narrow missing-A decision, not DNS packets/caches |
| AZ02-03 §03, Fig 5-2 | VNet links give resolution visibility; autoregistration is a separate VM-record function; custom/on-prem DNS needs forwarding or Private Resolver; a zone group manages PE records | Private DNS virtual network links; DNS integration scenarios | SOURCE-ANALYSED; resolver topology is design guidance, not a deployment |
| AZ02-03 §03 | Hub-spoke clients can share a zone through links; same-name independent zones don't merge; Microsoft warns about same-zone/multiple-PE A-record conflict | DNS integration scenarios; PE DNS zone values | SOURCE-ANALYSED; exact multi-PE design must be checked against the target service |
| AZ02-03 §04, Fig 5-3 | Storage PE does not automatically disable public access; PE network path, TLS hostname and Storage data authorization remain independent | Storage private endpoints; PE DNS zone values | SOURCE-ANALYSED; no TLS handshake or data request was run |
| AZ02-03 §05 | PE NIC effective routes/security rules aren't shown in Portal; inbound NSG flow logs unsupported; PE subnet network policies default disabled | Private endpoint overview; manage network policies | SOURCE-ANALYSED; region and feature limits must be checked before deployment |
| AZ02-03 §07 | Resolver visibility, private/public/NXDOMAIN answer, endpoint approval, public-network switch and separate data-authorization assertion | `labs/private-dns-model/dns_model.py`, scenario JSON and 18 tests | LOCAL_VERIFIED 2026-11-26 on Windows Python 3.13.9 and WSL; synthetic fixture, no DNS/API/network/TLS/Azure auth behavior modeled |
| AZ02-03 §08 | Future read-only inspection and active-probe procedure; Private Endpoint, DNS zone/query, Private Resolver and data processing have pricing dimensions | Azure CLI references; Azure DNS and Private Link pricing | DOCUMENTED; region/account offer not selected; no live cost estimate or deployment |

### Primary references

- https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview
- https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-dns
- https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-dns-integration
- https://learn.microsoft.com/en-us/azure/dns/private-dns-virtual-network-links
- https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints
- https://learn.microsoft.com/en-us/azure/private-link/disable-private-endpoint-network-policy
- https://learn.microsoft.com/en-us/cli/azure/network/private-endpoint?view=azure-cli-latest
- https://learn.microsoft.com/en-us/cli/azure/network/private-dns/link/vnet?view=azure-cli-latest
- https://learn.microsoft.com/en-us/cli/azure/network/private-dns/record-set/a?view=azure-cli-latest
- https://azure.microsoft.com/en-us/pricing/details/private-link/
- https://azure.microsoft.com/en-us/pricing/details/dns/

## AZ02-04 — Load Balancer, Application Gateway and Front Door

Research date: 2026-11-26. Current Microsoft Learn service, probe, routing, WAF, CLI and pricing sources were checked. The chapter scopes its experiment to documented decision rules and explicitly labels every local result as synthetic; no Azure traffic or cost was observed.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ02-04 §01, Fig 6-1 | Load Balancer is L4 TCP/UDP flow distribution; Application Gateway is regional and supports HTTP(S) L7 plus TCP/TLS L4 proxy; Front Door is global HTTP(S) edge delivery | Load Balancer overview and algorithm; Application Gateway components; Front Door overview and FAQ | SOURCE-ANALYSED; service selection is contextual; local model covers HTTP(S) routing only |
| AZ02-04 §02, Table 6-1, Fig 6-2 | LB TCP only checks a listener; LB HTTP(S) requires 200; Application Gateway default probe accepts 200–399 with host/path/backend-setting and HTTPS certificate behavior; Front Door requires 200 and evaluates an N-sample success threshold | LB health probes; Application Gateway health probes, backend health and troubleshooting; Front Door health probes | SOURCE-ANALYSED; no real probe request or backend-health report was observed |
| AZ02-04 §03, Fig 6-3 | LB defaults to five-tuple flow hashing; App Gateway rules bind listener, pool and backend settings; Front Door filters health then priority, latency sensitivity and weight; all unhealthy origins lead to documented round-robin fallback | LB algorithm; App Gateway components and routing rules; Front Door routing methods and health probes | SOURCE-ANALYSED; no actual request destination, latency or weight distribution measured |
| AZ02-04 §04 | Backend Health states, TLS diagnostics, WAF/request-path separation and read-only CLI command are distinct evidence sources | Application Gateway backend health and troubleshooting; WAF policy overview; Azure CLI reference | SOURCE-ANALYSED; CLI syntax checked only, not run in an Azure session |
| AZ02-04 §05 | TCP/HTTP/HTTPS status contracts, Application Gateway status/path/TLS assertion and Front Door sample/priority candidate set | labs/probe-model/probe_model.py, JSON fixture and 20 tests | LOCAL_VERIFIED 2026-11-26 on Windows Python 3.13.9; whole suite passed 83 tests in 6 directories on Windows and WSL; synthetic fixture, no HTTP/TCP/TLS/WAF/Front Door network or Azure control plane |
| AZ02-04 cost record | Application Gateway v2 fixed and capacity-unit dimensions, Front Door profile-hour/request/traffic dimensions and Load Balancer SKU/traffic pricing exist | Official Application Gateway, Front Door and Load Balancer pricing sources | DOCUMENTED; no region/SKU/account/runtime estimate; no live deployment or billing query |

### Primary references

- https://learn.microsoft.com/en-us/azure/load-balancer/load-balancer-overview
- https://learn.microsoft.com/en-us/azure/load-balancer/concepts
- https://learn.microsoft.com/en-us/azure/load-balancer/load-balancer-custom-probe-overview
- https://learn.microsoft.com/en-us/azure/application-gateway/application-gateway-components
- https://learn.microsoft.com/en-us/azure/application-gateway/configuration-request-routing-rules
- https://learn.microsoft.com/en-us/azure/application-gateway/application-gateway-probe-overview
- https://learn.microsoft.com/en-us/azure/application-gateway/application-gateway-backend-health
- https://learn.microsoft.com/en-us/troubleshoot/azure/application-gateway/application-gateway-backend-health-troubleshooting
- https://learn.microsoft.com/en-us/azure/application-gateway/ssl-overview
- https://learn.microsoft.com/en-us/azure/frontdoor/front-door-overview
- https://learn.microsoft.com/en-us/azure/frontdoor/front-door-faq
- https://learn.microsoft.com/en-us/azure/frontdoor/health-probes
- https://learn.microsoft.com/en-us/azure/frontdoor/routing-methods
- https://learn.microsoft.com/en-us/azure/web-application-firewall/ag/policy-overview
- https://learn.microsoft.com/en-us/azure/frontdoor/secure-front-door
- https://learn.microsoft.com/en-us/azure/application-gateway/understanding-pricing
- https://learn.microsoft.com/en-us/azure/frontdoor/billing
- https://azure.microsoft.com/en-us/pricing/details/load-balancer/
- https://learn.microsoft.com/en-us/cli/azure/network/application-gateway?view=azure-cli-latest

## AZ03-01 — Microsoft Entra ID, tokens and Azure RBAC

Research date: 2026-11-26. Primary references are Microsoft Learn, Microsoft identity platform, Azure Storage and Azure CLI documentation. The local program is a synthetic decision fixture, not an Azure or JWT implementation.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ03-01 §01, Fig 7-1 | Access-token audience identifies its intended recipient; API validators check their configured audience, issuer, tenant and token validity; access-token claim shape differs by token version | Microsoft identity platform access token and claims references | SOURCE-ANALYSED; the local model does not verify JWT signatures, signing keys, metadata or token-version variations |
| AZ03-01 §01–02 | Azure Storage Entra access involves identity authentication followed by service authorization; resource ID determines token audience; principal IDs are tenant-local Entra object IDs | Authorize Blob Access with Microsoft Entra ID; Azure RBAC role assignments | SOURCE-ANALYSED; the lecture covers Entra + RBAC only and does not model Shared Key, SAS or anonymous access |
| AZ03-01 §03, Fig 7-2 / Fig 7-3 | A role assignment binds principal, role definition and scope; parent assignments apply to descendants; role-definition AssignableScopes differs from assignment scope | Azure RBAC role assignments and scope overview | SOURCE-ANALYSED; actual tenant hierarchy and service scopes must be checked against resource IDs |
| AZ03-01 §03–04 | Actions/NotActions describe control-plane permissions; DataActions/NotDataActions describe data-plane permissions; not-lists subtract within one role and are not deny assignments | Azure RBAC role definitions | SOURCE-ANALYSED; deny assignments, role conditions, group/PIM state and service-specific decisions are outside the local model |
| AZ03-01 §05 | A valid Storage token audience does not itself grant blob-data access; matching DataActions and scope are needed for the Entra authorization path; role-change propagation may be delayed | Azure Storage Entra authorization and role definitions | SOURCE-ANALYSED; propagation bounds vary by scope and resource; no permission change or service call was observed |
| AZ03-01 §06 | Azure CLI can list role assignments with all, inherited and group assignments, and inspect a role definition | Azure CLI assignment and definition references | DOCUMENTED; command syntax checked only, not executed in an Azure session |
| AZ03-01 §07 | Synthetic trust assertion, issuer/tenant/audience/time checks, tenant+object principal match, scope ancestry, action planes and role-local exclusion/union | chapters/AZ03-01/labs/authorization-model and 17 unit tests | LOCAL_VERIFIED 2026-11-26; fixture logic only, no JWT, Azure, Entra, Graph or network calls |
| AZ03-01 cost / authorization | No Azure sign-in, token acquisition, role query, subscription query, mutation or billing request was made | Session and command execution record | LIVE_NOT_RUN; actual project billing remains NOT_VERIFIED |

### AZ03-01 primary references

- https://learn.microsoft.com/en-us/entra/identity-platform/access-token-claims-reference
- https://learn.microsoft.com/en-us/entra/identity-platform/access-tokens
- https://learn.microsoft.com/en-us/azure/storage/blobs/authorize-access-azure-active-directory
- https://learn.microsoft.com/en-us/azure/role-based-access-control/role-definitions
- https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments
- https://learn.microsoft.com/en-us/azure/role-based-access-control/scope-overview
- https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-list-cli
- https://learn.microsoft.com/en-us/cli/azure/role/assignment?view=azure-cli-latest
- https://learn.microsoft.com/en-us/cli/azure/role/definition?view=azure-cli-latest

## AZ03-02 — Managed Identity, Key Vault and Workload Identity Federation

Research date: 2026-11-26. Claims use Microsoft Learn and the Microsoft REST API reference as primary sources. The Python SDK sample is documented but was not executed against Azure. The local model uses fictional claims and symbolic permissions; it is not a token, identity, network, or Key Vault emulator.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ03-02 §01, Fig 8-1 | System-assigned identity lifecycle follows its Azure host; UAMI lifecycle is independent and can be shared; identity security boundary is the attached resource | Managed identities overview; developer guidance; FAQ | SOURCE-ANALYSED; no identity was created or inspected |
| AZ03-02 §01 | IMDS default selection depends on system identity and attached UAMIs; explicit selection is recommended even when one UAMI is currently attached; VM token `resource` is the target App ID URI and appears as token audience; `Metadata: true` is required | Managed identities FAQ; VM token acquisition | SOURCE-ANALYSED; no IMDS call or token was requested |
| AZ03-02 §01 | Azure Identity `ManagedIdentityCredential` accepts a UAMI client ID; Key Vault `SecretClient` accepts the credential and vault URL | Azure Identity Python reference; Key Vault Secrets SDK | DOCUMENTED; code shape checked against current API docs, not executed |
| AZ03-02 §02, Fig 8-2 | External workload assertion is exchanged for an Entra access token after federated trust; `issuer`, `subject`, and `audience` must match; matching is case-sensitive; common external audience is `api://AzureADTokenExchange` | Workload identity federation; FIC considerations; identity platform breaking changes | SOURCE-ANALYSED; no real OIDC assertion or Entra exchange was used |
| AZ03-02 §02 | External assertion audience and final Key Vault access-token audience identify different receivers; Key Vault resource audience is `https://vault.azure.net` and REST API scope is `https://vault.azure.net/.default` | Key Vault authentication requests/responses; Key Vault REST API reference | SOURCE-ANALYSED; no access token was acquired or decoded |
| AZ03-02 §03, Fig 8-3 | Key Vault control and data planes use Entra authentication but independent authorization; Contributor is control plane only; Secrets User reads secret content; RBAC mode invalidates legacy access policies | Key Vault RBAC guide; RBAC migration | SOURCE-ANALYSED; no role assignment or permission model was queried or changed |
| AZ03-02 §03–05 | Vault network/firewall/private endpoint path is an independent gate from token audience and data authorization; a denied request is not by itself proof of missing RBAC | Key Vault network security; authentication requests/responses | SOURCE-ANALYSED; model reduces network to a boolean and does not issue a request |
| AZ03-02 §05 | Synthetic identity selection, exact FIC claim match, Key Vault audience/tenant/principal match, network result, and a small role/access-policy mapping | chapters/AZ03-02/labs/credential-flow and 16 tests | LOCAL_VERIFIED 2026-11-26; fixture logic only; full Windows and WSL suites each passed 116 tests in 8 lab directories |
| AZ03-02 cost / authorization | No real token acquisition, Azure/Entra/Graph/IMDS/OIDC request, Key Vault read, network query, role query/change, resource operation or billing request | Session and command execution record | LIVE_NOT_RUN; actual project billing remains NOT_VERIFIED |

### AZ03-02 primary references

- https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview
- https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview-for-developers
- https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/managed-identities-faq
- https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/how-to-use-vm-token
- https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.managedidentitycredential?view=azure-python
- https://learn.microsoft.com/en-us/python/api/overview/azure/keyvault-secrets-readme
- https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation
- https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation-considerations
- https://learn.microsoft.com/en-us/entra/identity-platform/reference-breaking-changes#august-2024
- https://learn.microsoft.com/en-us/azure/key-vault/general/authentication-requests-and-responses
- https://learn.microsoft.com/en-us/rest/api/keyvault/secrets/get-secrets/get-secrets
- https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide
- https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-migration
- https://learn.microsoft.com/en-us/azure/key-vault/general/network-security
- https://learn.microsoft.com/en-us/cli/azure/role/assignment?view=azure-cli-latest

## AZ03-03 — Azure Policy, Activity Log and Defender for Cloud

Research date: 2026-11-26. Claims are grounded in current Microsoft Learn primary documentation. Three original source-generated diagrams and a synthetic fixture distinguish governance effect, telemetry evidence, and security posture. No Azure query or feature enablement was performed.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ03-03 §02, Fig 9-1 | Audit reports matching non-compliance without itself denying; Deny is evaluated before the Resource Provider in applicable Resource Manager requests; deployIfNotExists follows provider success after a configurable delay and requires assignment identity for remediation | Azure Policy effect basics; compliance states; deployIfNotExists and remediation guidance | SOURCE-ANALYSED; fixture models three effects and create/update/existing phases, not real policy JSON, mode, alias, assignment scope or provider outcomes |
| AZ03-03 §03, Fig 9-2 | Activity Log covers control-plane events, reads are not typically captured, and ARM authentication/authorization rejection before operation start creates no entry or Activity Log alert; resource logs cover data-plane behavior and require diagnostic settings; default Activity Log retention is 90 days | Activity Log overview; Azure Activity Log event schema; Activity Log retrieval guide | SOURCE-ANALYSED; no query or diagnostic setting was run; local classifier describes only broad event classes |
| AZ03-03 §04, Fig 9-3 | Defender for Cloud assesses posture and yields MCSB recommendations; only a subset supports Deny/Enforce through Azure Policy; Enforce uses deployIfNotExists; foundational CSPM is distinct from optional paid plans; Secure Score models can differ by portal | Defender for Cloud overview; MCSB recommendations; policy reference; Secure Score; connect subscription and plan pricing docs | SOURCE-ANALYSED; no Defender plan, recommendation effect, or service was enabled; no cost estimate |
| AZ03-03 §06 | Synthetic Policy-effect timing, event visibility, diagnostic-setting state, recommendation/effect separation, and plan-price review indicator | chapters/AZ03-03/labs/governance-evidence-model and 16 tests | LOCAL_VERIFIED 2026-11-26; Windows targeted and full suite passed; WSL full suite passed 132 tests in 9 directories; fixture only |
| AZ03-03 §07 | Azure CLI templates for Policy state and Activity Log retrieval, limited to approved read scopes | Azure CLI policy state list; Activity Log query guide | DOCUMENTED; commands were not run; Stage 3 L0 and explicit live-query authorization remain required |
| AZ03-03 cost / authorization | No Azure sign-in, subscription query, policy-state query, Activity Log query, Defender enablement, resource operation or billing query was performed | Session and command execution record | LIVE_NOT_RUN; actual cumulative spend remains NOT_VERIFIED |

### AZ03-03 primary references

- https://learn.microsoft.com/en-us/azure/governance/policy/concepts/effect-basics
- https://learn.microsoft.com/en-us/azure/governance/policy/concepts/compliance-states
- https://learn.microsoft.com/en-us/azure/governance/policy/concepts/effect-deploy-if-not-exists
- https://learn.microsoft.com/en-us/azure/governance/policy/how-to/remediate-resources
- https://learn.microsoft.com/en-us/azure/azure-monitor/fundamentals/activity-log
- https://learn.microsoft.com/en-us/azure/azure-monitor/platform/activity-log-schema
- https://learn.microsoft.com/en-us/azure/azure-monitor/platform/activity-log-view
- https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-cloud-introduction
- https://learn.microsoft.com/en-us/azure/defender-for-cloud/secure-score-security-controls
- https://learn.microsoft.com/en-us/azure/defender-for-cloud/manage-mcsb
- https://learn.microsoft.com/en-us/azure/defender-for-cloud/policy-reference
- https://learn.microsoft.com/en-us/azure/defender-for-cloud/connect-azure-subscription
- https://learn.microsoft.com/en-us/cli/azure/policy/state?view=azure-cli-latest

## AZ04-01 — VM, VMSS, Managed Disk and Operations

Research date: 2026-11-26. Microsoft Learn primary documentation grounds Azure behavior. State, probe, monitoring, and performance examples in the lab are synthetic and intentionally narrow.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ04-01 §01, Fig 10-1 | Power state and provisioning state answer different questions and can coexist; Stopped (Allocated) bills for VM instance usage, while deallocated VM instance usage is not billed and attached resources may still cost | VM states and billing status | SOURCE-ANALYSED; billing table is not a live account check or SKU quote |
| AZ04-01 §01, Fig 10-1 | Host metrics are available by default; guest OS metrics/logs generally require Azure Monitor Agent and an associated DCR; a host signal is not an app health assertion | Monitor Azure virtual machines; VM data collection | SOURCE-ANALYSED; collection is configuration- and workload-dependent |
| AZ04-01 §01, Fig 10-1 | Boot diagnostics exposes boot serial log and screenshot evidence; it is not an application availability check | Azure boot diagnostics | SOURCE-ANALYSED; access prerequisites and evidence availability depend on the current service path |
| AZ04-01 §02–03, Fig 10-2 | Uniform and Flexible orchestration differ in how instances are represented and managed; the mode is selected at creation; manual, automatic, and rolling policies describe different update timing and health-gate behavior | VMSS orchestration modes; VMSS upgrade policy; Application Health Extension | SOURCE-ANALYSED; the current upgrade-policy article describes Flexible rolling with the extension, while the orchestration article's unsupported-parameters section says the VMSS upgrade-policy parameter must be null/empty for Flexible. The chapter flags this current primary-source conflict and requires mode/API-specific confirmation. |
| AZ04-01 §03, Fig 10-3 | Managed disks and VM sizes each have IOPS/throughput limits; the uncached remote path uses disk-level and VM-level budgets | VM and managed disk performance | SOURCE-ANALYSED; the min-of-three formula applies only to the explicitly simplified one-disk, uncached, no-burst teaching model, not a general Azure performance guarantee |
| AZ04-01 §04 | `az vm get-instance-view` is a documented read-only command template | Azure CLI az vm reference | DOCUMENTED; not run; future use requires Stage 3 L0 and authorized scope |
| AZ04-01 §05 | Synthetic state separation, guest-collection gate, VMSS policy branches, single-disk I/O ceilings, and boot/app evidence boundary | `chapters/AZ04-01/labs/vm-operations-model` and 18 unit tests | LOCAL_VERIFIED 2026-11-26; deterministic fixture only; full Windows and WSL suites each passed 150 tests across 10 lab directories |
| AZ04-01 cost / authorization | No Azure authentication, subscription/monitoring query, CLI operation, resource mutation, deployment, network probe, or billing query was performed | Session and command execution record | LIVE_NOT_RUN; actual cumulative spend remains NOT_VERIFIED |

### AZ04-01 primary references

- https://learn.microsoft.com/en-us/azure/virtual-machines/states-billing
- https://learn.microsoft.com/en-us/azure/virtual-machines/monitor-vm
- https://learn.microsoft.com/en-us/azure/virtual-machines/boot-diagnostics
- https://learn.microsoft.com/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-orchestration-modes
- https://learn.microsoft.com/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-upgrade-policy
- https://learn.microsoft.com/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-health-extension
- https://learn.microsoft.com/en-us/azure/virtual-machines/disks-performance
- https://learn.microsoft.com/en-us/cli/azure/vm?view=azure-cli-latest

## AZ04-02 — App Service, Container Apps and Deployment

Research date: 2026-11-26. Microsoft Learn is the primary source for service behavior. All release paths drawn in the figures are explanatory, and all lab outputs are generated from local synthetic fixtures.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ04-02 §01, Fig 11-1 | App Service slots are live apps with hostnames and plan-tier prerequisites; Container Apps revisions are template updates governed by revision mode and ingress weights | App Service deployment slots; Container Apps revisions | SOURCE-ANALYSED; not a live deployment or cost estimate |
| AZ04-02 §02, Fig 11-2 | Slot swap prepares source with target slot-specific settings, restarts and warms source, then swaps routing; default warm-up accepts any HTTP response unless valid statuses are configured; slot identity is not swapped | App Service deployment slots; App Service managed identity | SOURCE-ANALYSED; no swap, identity, or endpoint was queried |
| AZ04-02 §02, Fig 11-2 | App Service Health Check is a per-instance load-balancer signal and is not the swap warm-up gate; its configuration is not slot-specific and follows the swap | App Service Health Check; deployment slots | SOURCE-ANALYSED; configuration and runtime behavior depend on app, plan, and instance count |
| AZ04-02 §03, Fig 11-3 | Container Apps template changes create a revision; secrets, ingress, traffic, mode and registry configuration are app-wide; identity updates do not create a new revision or automatically restart the app | Container Apps revisions; ingress; managed identity; deployment troubleshooting | SOURCE-ANALYSED; rollback of routes does not restore global configuration or data |
| AZ04-02 §04, Fig 11-4 | Single mode routes after provisioning, scale and startup/readiness conditions; multiple mode exposes operator-managed weights; probes and app-level smoke tests answer different questions | Container Apps revisions; health probes; traffic splitting | SOURCE-ANALYSED; probe success is not a business SLI assertion |
| AZ04-02 §04 | Ingress visibility, transport and target port are separate from revision scaling and readiness | Container Apps ingress; scaling | SOURCE-ANALYSED; no port, ingress, or scale behavior was live-tested |
| AZ04-02 §05 | `az webapp deployment slot list` and `az containerapp revision list` are documented future read-only templates | App Service deployment slot CLI; Container Apps revision CLI documentation | DOCUMENTED; not run; Stage 3 L0 and specific query authorization remain required |
| AZ04-02 §06 | Local model covers slot warm-up and route movement, config scope, revision cutover weights and route-only rollback | `chapters/AZ04-02/labs/app-release-model` and 16 unit tests | LOCAL_VERIFIED 2026-11-26; fixture only; Windows and WSL full suites each passed 166 tests across 11 lab directories |
| AZ04-02 cost / authorization | No Azure sign-in, subscription query, CLI execution, resource operation, probe, token request or billing query was performed | Session and command execution record | LIVE_NOT_RUN; actual cumulative spend remains NOT_VERIFIED |

### AZ04-02 primary references

- https://learn.microsoft.com/en-us/azure/app-service/deploy-staging-slots
- https://learn.microsoft.com/en-us/azure/app-service/monitor-instances-health-check
- https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity
- https://learn.microsoft.com/en-us/azure/container-apps/revisions
- https://learn.microsoft.com/en-us/azure/container-apps/health-probes
- https://learn.microsoft.com/en-us/azure/container-apps/traffic-splitting
- https://learn.microsoft.com/en-us/azure/container-apps/ingress-how-to
- https://learn.microsoft.com/en-us/azure/container-apps/scale-app
- https://learn.microsoft.com/en-us/azure/container-apps/managed-identity
- https://learn.microsoft.com/en-us/azure/container-apps/troubleshoot-deployment-errors

## AZ04-03 — AKS and ACR Readiness

Research date: 2026-11-26. Microsoft Learn is the primary source. The lab is an offline deterministic model; it does not interact with AKS, ACR, Azure, Kubernetes, Docker, DNS, or network endpoints.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ04-03 §01–02, Fig 12-1 | Azure manages the AKS control plane; node pools host kubelet and container runtime. Control-plane identity, kubelet image-pull identity, and pod workload identity have separate callers and permissions | AKS core concepts; AKS managed identities; AKS-ACR authentication; Workload ID | SOURCE-ANALYSED; identity paths are documented, no identity/token/role was queried |
| AZ04-03 §03–04, Fig 12-2 | Azure CNI Overlay separates VNet node addresses from pod CIDR; outbound SNAT and CoreDNS forwarding do not remove the need to validate NSG, DNS, and registry routes | Azure CNI Overlay; AKS DNS concepts | SOURCE-ANALYSED; network diagram is explanatory, no packet or DNS request was made |
| AZ04-03 §05, Fig 12-3 | Pod requests, selectors, affinity, taints and tolerations constrain scheduling; HPA changes pod count while Cluster Autoscaler can add feasible node capacity for unscheduled constrained pods | AKS scheduler best practices; Cluster Autoscaler overview | SOURCE-ANALYSED; interaction is a documented synthesis, not a measured control-loop timing guarantee |
| AZ04-03 §06, Fig 12-4 | Startup, readiness, and liveness answer different health questions; a running pod can remain unready and absent from Service endpoints | AKS cluster reliability and probes; AKS DNS concepts | SOURCE-ANALYSED; probe behavior was not tested on a Kubernetes cluster |
| AZ04-03 §07, Fig 12-5 | AKS-ACR image pulls use kubelet identity; RBAC-only and ABAC repository-permission modes use different roles, and catalog listing is a separate permission | AKS-ACR authentication; ACR ABAC repository permissions; ACR troubleshooting | SOURCE-ANALYSED; no role assignment or image pull occurred |
| AZ04-03 §08 | Control-plane and node-pool upgrade options, version skew, PDB eviction constraints and surge capacity form separate upgrade gates | AKS node-pool upgrades; AKS upgrade options | SOURCE-ANALYSED; available target versions and quotas are subscription/region-specific and must be rechecked before live work |
| AZ04-03 §09 | Future read-only commands are documented as templates; the local model maps fixture evidence to likely failure domains | AKS core concepts; `chapters/AZ04-03/labs/aks-readiness-model` | LOCAL_VERIFIED after Windows and WSL offline suites; the model does not establish live AKS behavior |
| AZ04-03 cost / authorization | No Azure sign-in, subscription query, Azure CLI request, cluster operation, network/DNS probe, token request, resource mutation or billing query was performed. Docker availability was checked locally; `kind get clusters` could not connect to the Docker engine, and `kubectl config get-contexts` was a read-only local inventory with no context selected or changed | Session and command execution record | LIVE_NOT_RUN; actual cumulative spend remains NOT_VERIFIED |

### AZ04-03 primary references

- https://learn.microsoft.com/en-us/azure/aks/core-aks-concepts
- https://learn.microsoft.com/en-us/azure/aks/best-practices-app-cluster-reliability
- https://learn.microsoft.com/en-us/azure/aks/intro-aks-automatic
- https://learn.microsoft.com/en-us/azure/aks/cluster-container-registry-integration
- https://learn.microsoft.com/en-us/azure/aks/workload-identity-overview
- https://learn.microsoft.com/en-us/azure/aks/managed-identity-overview
- https://learn.microsoft.com/en-us/azure/aks/concepts-network-azure-cni-overlay
- https://learn.microsoft.com/en-us/azure/aks/dns-concepts
- https://learn.microsoft.com/en-us/troubleshoot/azure/azure-kubernetes/connectivity/cannot-pull-image-from-acr-to-aks-cluster
- https://learn.microsoft.com/en-us/azure/aks/operator-best-practices-advanced-scheduler
- https://learn.microsoft.com/en-us/azure/aks/cluster-autoscaler-overview
- https://learn.microsoft.com/en-us/azure/container-registry/container-registry-rbac-abac-repository-permissions
- https://learn.microsoft.com/en-us/azure/aks/upgrade-node-pools
- https://learn.microsoft.com/en-us/azure/aks/upgrade-options

## AZ04-04 — Azure Storage and Azure SQL data boundaries

Research date: 2026-11-27. Microsoft Learn is the primary source. The lab is an offline synthetic decision model; it does not call Azure, query DNS, connect to Storage or SQL, or restore data.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ04-04 §01, Fig 13-1 | Read requests pass through DNS/endpoint, network, authentication/data authorization, and object/database state gates; failures at one gate do not establish the next | Storage network security FAQ; Azure SQL network controls; Blob authorization; SQL Entra authentication | SOURCE-ANALYSED; no client request or identity was observed |
| AZ04-04 §02, Fig 13-2 | Storage PE routes a normal service FQDN to a private IP through DNS; PE target subresources differ; Storage firewall applies to the public endpoint, while a service endpoint still uses it | Storage private endpoints; private endpoint DNS; Storage network security | SOURCE-ANALYSED; no DNS, PE, route, firewall or service endpoint was queried |
| AZ04-04 §03, Fig 13-3 | ARM resource roles are distinct from Blob data roles; `listKeys` permission can permit Shared Key access if allowed; SAS/key authorization does not provide network reachability | Blob authorization with Microsoft Entra ID; Storage data authorization | SOURCE-ANALYSED; no role assignment, key, SAS or token was used |
| AZ04-04 §04, Fig 13-4 | SQL PE does not disable public access by itself; private DNS, Redirect/Proxy transport, Entra authentication, SQL principal and database grants are separate checks | Azure SQL Private Link; connectivity architecture; Entra authentication; connection troubleshooting | SOURCE-ANALYSED; connection policy, ports, DNS, identities and database grants remain unqueried |
| AZ04-04 §05, Fig 13-5 | Blob versioning/PITR has resource and feature constraints; SQL PITR, geo-restore and LTR use different windows and backup requirements, and backup restores create a new database | Storage data protection; Blob versioning and PITR; SQL automated backups, restore and RTO/RPO | SOURCE-ANALYSED; current protection settings and recoverable backup inventory are unverified |
| AZ04-04 §06 | Lab classifies 28 synthetic Storage/SQL read and recovery cases with 30 unit tests | `chapters/AZ04-04/labs/data-boundary-model` | LOCAL_VERIFIED 2026-11-27; Windows and WSL suites each passed 217 tests across 13 directories; no service emulation |
| AZ04-04 cost / authorization | No Azure authentication, control/data-plane query, DNS or network probe, Storage/SQL request, token, restore, resource mutation or billing query was performed | Session and command execution record | LIVE_NOT_RUN; actual cumulative spend remains NOT_VERIFIED |

### AZ04-04 primary references

- https://learn.microsoft.com/en-us/troubleshoot/azure/azure-storage/blobs/networking/storage-network-security-faq
- https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints
- https://learn.microsoft.com/en-us/azure/networking/design-guide/dns-security
- https://learn.microsoft.com/en-us/azure/storage/blobs/authorize-access-azure-active-directory
- https://learn.microsoft.com/en-us/azure/storage/common/authorize-data-access?tabs=blobs
- https://learn.microsoft.com/en-us/azure/azure-sql/database/private-endpoint-overview
- https://learn.microsoft.com/en-us/azure/azure-sql/database/connectivity-architecture
- https://learn.microsoft.com/en-us/azure/azure-sql/database/authentication-aad-overview
- https://learn.microsoft.com/en-us/azure/storage/blobs/data-protection-overview
- https://learn.microsoft.com/en-us/azure/storage/blobs/versioning-overview
- https://learn.microsoft.com/en-us/azure/storage/blobs/point-in-time-restore-overview
- https://learn.microsoft.com/en-us/azure/azure-sql/database/automated-backups-overview
- https://learn.microsoft.com/en-us/azure/azure-sql/database/recovery-using-backups
- https://learn.microsoft.com/en-us/azure/azure-sql/database/business-continuity-high-availability-disaster-recover-hadr-overview
- https://learn.microsoft.com/en-us/azure/azure-sql/database/troubleshoot-common-errors-issues

## AZ05-01 — Azure Monitor metrics and alerts

Research date: 2026-11-27. Microsoft Learn is the primary source. The lab is an offline evaluator for synthetic metric buckets; it does not call Azure Monitor or reproduce the platform's provider-side metrics pipeline or dynamic-threshold model.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ05-01 §01, Fig 14-1 | Metrics are time-series values associated with a resource, namespace/name and dimensions; alert detection and downstream response are distinct stages | Metrics data platform; alert rule creation; alert processing rules | SOURCE-ANALYSED; diagram is an explanatory synthesis, no metric or alert was queried |
| AZ05-01 §02, Fig 14-2 | Average may hide a hot member; Max and per-dimension evaluation answer different questions; Count is record count, while aggregation must match provider metric semantics | Metrics aggregation/display; create metric alert rule; metric-alert troubleshooting | SOURCE-ANALYSED; examples use synthetic values and do not describe a particular Azure resource metric |
| AZ05-01 §03, Fig 14-3 | Check frequency controls how often a rule evaluates; aggregation granularity/lookback controls the data period considered; charts and rules should be aligned when troubleshooting | Create metric alert rule; metric-alert troubleshooting; metrics aggregation/display | SOURCE-ANALYSED; half-open windows are an explicit lab abstraction, not a claim about raw Azure bucket internals |
| AZ05-01 §04, Fig 14-4 | Static thresholds use an operator/value; dynamic thresholds learn historical patterns and have minimum sample/history and longer seasonality requirements | Create metric alert rule; dynamic thresholds | SOURCE-ANALYSED; the lab only classifies sample-history readiness and does not train or predict Azure thresholds |
| AZ05-01 §05, Fig 14-5 | Stateful/stateless monitor condition behavior is separate from user response state and from action/processing-rule handling | Alerts overview; alert types; alert processing rules | SOURCE-ANALYSED; no notification, action group or processing rule was created or changed |
| AZ05-01 §06–08 | 11 synthetic fixtures and 23 tests cover aggregation, dimensions, windows, state transitions, suppression and dynamic-history gates | `chapters/AZ05-01/labs/metric-alert-model` | LOCAL_VERIFIED 2026-11-27; Windows and WSL suites each passed 240 tests across 14 directories; no service emulation |
| AZ05-01 cost / authorization | No Azure sign-in, metric query, alert/action configuration, notification, resource mutation or billing query was performed | Session and command execution record | LIVE_NOT_RUN; actual cumulative spend remains NOT_VERIFIED |

### AZ05-01 primary references

- https://learn.microsoft.com/en-us/azure/azure-monitor/metrics/data-platform-metrics
- https://learn.microsoft.com/en-us/azure/azure-monitor/metrics/metrics-aggregation-explained
- https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-create-metric-alert-rule
- https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-troubleshoot-metric
- https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-dynamic-thresholds
- https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-overview
- https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-types
- https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-processing-rules

## AZ05-02 — Log Analytics, KQL and Application Insights

Research date: 2026-11-27. Microsoft Learn is the primary source. The lab evaluates synthetic, workspace-based telemetry rows and teaches selected KQL query shapes; it neither executes KQL nor sends telemetry to Azure.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ05-02 §01, Fig 15-1 | Workspaces store log rows in tables with schema; Azure resource diagnostics and Application Insights application instrumentation are distinct collection paths; table plan and retention affect access and query considerations | Log tables; Log Analytics queries; AppRequests/AppDependencies/AppExceptions table references | SOURCE-ANALYSED; no workspace, diagnostic setting, table plan or ingestion was queried |
| AZ05-02 §02, Fig 15-2 | KQL begins with a table, is case-sensitive in Azure Monitor, and uses piped operators; constrain time and table scope, filter early, and apply time bounds to each union/join branch | Get started with log queries; query optimization; KQL `summarize` operator | SOURCE-ANALYSED; KQL examples are documented templates and were not sent to a workspace |
| AZ05-02 §03, Fig 15-3 | Workspace-based Application Insights separates requests, dependencies and exceptions; `OperationId` associates telemetry with a logical operation and `ParentId`/available item IDs help inspect direct parentage; AppExceptions does not expose the same row `Id` column in its current table reference | AppRequests, AppDependencies, AppExceptions table references | SOURCE-ANALYSED; table/column availability is workspace/schema-specific; no trace was queried |
| AZ05-02 §04 | Application Map shows component topology and hotspots; transaction diagnostics supports end-to-end request/dependency investigation; correlation does not alone establish root cause | Dependency tracking; Application Map; failures/performance/transactions | SOURCE-ANALYSED; diagram and scenario are illustrative, no application was instrumented |
| AZ05-02 §05, Fig 15-5 | Sampled telemetry rows can represent multiple events; `ItemCount` should be included in request-count aggregation; sampling is not proof that all dependencies/spans were collected | Application Insights metrics and sampling; AppRequests sample queries | SOURCE-ANALYSED; synthetic weighting only, no SDK sampling or data loss was observed |
| AZ05-02 §05 | Current language recommendations differ between Microsoft OpenTelemetry Distro for .NET/Node.js/Python and Azure Monitor OpenTelemetry Distro for Java; do not initialize both in one application | Enable OpenTelemetry; OpenTelemetry sampling | SOURCE-ANALYSED 2026-11-27; recheck language and SDK guidance before live implementation |
| AZ05-02 §06–07 | Five synthetic cases and 11 tests cover weighted request counts, time filtering, operation grouping, direct parent links, and missing visible parent records | `chapters/AZ05-02/labs/telemetry-triage` | LOCAL_VERIFIED 2026-11-27; Windows and WSL suites each passed 251 tests across 15 directories; no KQL/service emulation |
| AZ05-02 cost / authorization | No Azure authentication, workspace/resource query, telemetry export, resource mutation or billing request was performed | Session and command execution record | LIVE_NOT_RUN; actual cumulative spend remains NOT_VERIFIED |

### AZ05-02 primary references

- https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-table-overview
- https://learn.microsoft.com/en-us/azure/azure-monitor/logs/get-started-queries
- https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/apprequests
- https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/appdependencies
- https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/appexceptions
- https://learn.microsoft.com/en-us/azure/azure-monitor/logs/query-optimization
- https://learn.microsoft.com/en-us/kusto/query/summarize-operator?view=azure-data-explorer
- https://learn.microsoft.com/en-us/azure/azure-monitor/app/metrics-overview
- https://learn.microsoft.com/en-us/azure/azure-monitor/reference/queries/apprequests
- https://learn.microsoft.com/en-us/azure/azure-monitor/app/dependencies
- https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-map
- https://learn.microsoft.com/en-us/azure/azure-monitor/app/failures-performance-transactions
- https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-sampling
- https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable

## AZ05-03 — Azure CLI, PowerShell and Resource Graph

Research date: 2026-11-27. Microsoft Learn is the primary source. The local lab evaluates only a synthetic asset fixture; it neither authenticates nor queries Azure.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ05-03 §01, Fig 16-1 | CLI account selection, Az PowerShell context, explicit Resource Graph scope and per-resource RBAC `read` permissions jointly bound visibility; no returned row does not prove absence | Azure CLI account reference; Azure PowerShell contexts; Resource Graph scope and overview | SOURCE-ANALYSED; no account, subscription, context or authorization was queried |
| AZ05-03 §02, Fig 16-2 | `az resource list`/`Get-AzResource` are ARM resource-list paths; `az graph query -q`/`Search-AzGraph -Query` use Resource Graph KQL; CLI global `--query` is JMESPath | Azure CLI `az resource`; Azure CLI `az graph`; Search-AzGraph | SOURCE-ANALYSED; command templates were not executed |
| AZ05-03 §03, Fig 16-3 | Resource Graph is an indexed exploration service, supports explicit subscription/management-group scope, and may lag ARM changes; query projection and order determine the inventory's meaning | Resource Graph overview; query language; Azure CLI and PowerShell command references | SOURCE-ANALYSED; no live index, provider response or scope was observed |
| AZ05-03 §04, Fig 16-4 | Resource Graph pages cap at 1,000; continuation token can be unavailable for `take`/`limit`/`sample` or all-dynamic/null projections; stable unique-ID sorting improves repeatability but changing data can shift offset pages | Guidance for pagination; Azure CLI `az graph`; Search-AzGraph | SOURCE-ANALYSED; local offset deletion scenario is a simplified synthetic model, not service-token behavior |
| AZ05-03 §05, Fig 16-5 | A defensible completeness claim records identity, tenant, exact scope, read permissions, index freshness, paging status, timestamps, query and duplicate/missing-ID checks; large scope can be throttled or subscription-limited | Resource Graph overview; query-language scope; pagination; throttling guidance | SOURCE-ANALYSED; no live tenant, throttling header, billing or completeness claim was checked |
| AZ05-03 §06–07 | Seven synthetic resources, explicit subscription allowlist, unreadable fixture objects, stable sort and page audit; 13 local tests include duplicate/missing/unexpected IDs and offset drift after deletion | `chapters/AZ05-03/labs/inventory-model` | LOCAL_VERIFIED 2026-11-27; Windows and WSL suites each passed 264 tests across 16 directories; no Azure/KQL/ARM emulation |
| AZ05-03 cost / authorization | No Azure authentication, subscription/context enumeration, Resource Graph query, ARM list, resource mutation or billing request was performed | Session and command execution record | LIVE_NOT_RUN; actual cumulative spend remains NOT_VERIFIED |

### AZ05-03 primary references

- https://learn.microsoft.com/en-us/cli/azure/account
- https://learn.microsoft.com/en-us/powershell/azure/context-persistence?view=azps-17.0.0
- https://learn.microsoft.com/en-us/azure/governance/resource-graph/concepts/query-language
- https://learn.microsoft.com/en-us/azure/governance/resource-graph/overview
- https://learn.microsoft.com/en-us/azure/governance/resource-graph/concepts/paging-results
- https://learn.microsoft.com/en-us/azure/governance/resource-graph/concepts/guidance-for-throttled-requests
- https://learn.microsoft.com/en-us/cli/azure/graph?view=azure-cli-latest
- https://learn.microsoft.com/en-us/powershell/module/az.resourcegraph/search-azgraph?view=azps-17.0.0
- https://learn.microsoft.com/en-us/cli/azure/resource?view=azure-cli-latest
- https://learn.microsoft.com/en-us/azure/governance/resource-graph/troubleshoot/general

## AZ06-01 — Azure Backup, recovery and Site Recovery

Research date: 2026-11-27. Microsoft Learn is the primary source. The offline lab evaluates six synthetic recovery cases and makes no Azure request.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ06-01 §01, Fig 17-1 | Azure Backup retains policy-governed recovery points while Site Recovery replicates changes and orchestrates failover; their recovery objectives differ | Azure Backup architecture; Azure-to-Azure Site Recovery architecture | SOURCE-ANALYSED; no vault, protected VM, replication stream or recovery plan was inspected |
| AZ06-01 §02, Fig 17-2 | Application, file-system and crash consistency imply different recovery expectations; a consistency label alone does not prove application or ledger correctness | About Azure VM backup; Backup architecture | SOURCE-ANALYSED; consistency outcomes are taught from documentation and checked only with synthetic fixture fields |
| AZ06-01 §03, Fig 17-3 | VM recovery can target a new/alternate location, disks, original location or files; restore scope changes overwrite and validation risks | About the Azure VM restore process; recovery-point management | SOURCE-ANALYSED; restore options were not invoked |
| AZ06-01 §04 | Backup vault security, redundancy, cross-region restore and retention have workload/region constraints and do not by themselves prove application recovery | Azure Backup reliability; secure Azure Backup deployment; Backup guidance and enhanced policy | SOURCE-ANALYSED; no vault setting, region support, retention policy or price was queried |
| AZ06-01 §05, Fig 17-4 | Site Recovery `Latest` can process delivered pending data for a newer point; `Latest processed` uses already processed data; test failover, cleanup, reprotect and failback are distinct lifecycle steps | Azure-to-Azure disaster recovery architecture; Site Recovery failover and common questions; test failover; recovery plans | SOURCE-ANALYSED; local cases model only the stated timing trade-off and isolation/cleanup gates |
| AZ06-01 §05–06, Fig 17-5 | Operational RPO is measured from business failure/data-loss start to recovery-point time; this chapter's measured RTO contract runs from disruption to verified service, including detection and recovery-start delay | Recovery-point management; Site Recovery failover and recovery plans; chapter's explicit measurement contract | SOURCE-ANALYSED + locally specified acceptance definition; no Azure SLA or workload objective is claimed |
| AZ06-01 §06–07 | Six synthetic cases exercise numeric RPO/RTO objectives, integrity, row count, application probe, failover isolation and cleanup; 16 tests cover time arithmetic and recovery acceptance | `chapters/AZ06-01/labs/recovery-model` | LOCAL_VERIFIED 2026-11-27; Windows and WSL suites each passed 280 tests across 17 directories; no Azure service emulation |
| AZ06-01 cost / authorization | No Azure sign-in, identity/context enumeration, Backup/Site Recovery call, restore, resource operation, network probe or billing request was performed | Session and command execution record | LIVE_NOT_RUN; actual cumulative spend remains NOT_VERIFIED |

### AZ06-01 primary references

- https://learn.microsoft.com/en-us/azure/backup/backup-azure-vms-introduction
- https://learn.microsoft.com/en-us/azure/backup/backup-architecture
- https://learn.microsoft.com/en-us/azure/backup/about-azure-vm-restore
- https://learn.microsoft.com/en-us/azure/reliability/reliability-backup
- https://learn.microsoft.com/en-us/azure/backup/secure-backup
- https://learn.microsoft.com/en-us/azure/backup/guidance-best-practices
- https://learn.microsoft.com/en-us/azure/backup/backup-azure-vms-enhanced-policy
- https://learn.microsoft.com/en-us/azure/site-recovery/azure-to-azure-architecture
- https://learn.microsoft.com/en-us/azure/site-recovery/site-recovery-failover
- https://learn.microsoft.com/en-us/azure/site-recovery/azure-to-azure-common-questions
- https://learn.microsoft.com/en-us/azure/backup/manage-recovery-points
- https://learn.microsoft.com/en-us/azure/site-recovery/site-recovery-test-failover-to-azure
- https://learn.microsoft.com/en-us/azure/site-recovery/recovery-plan-overview

## AZ06-02 — Incident Response, RCA and integrated banking case

Research date: 2026-11-27. Microsoft Learn is the primary source for Azure service behavior. The banking incident and every observation, role change, timeline and recovery result in the lab are synthetic.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ06-02 §01, Fig 18-1 | Incident response needs explicit ownership, escalation, impact-based triage, containment, recovery checks, communication and controlled closure; RCA/postmortem turn evidence into improvements | Azure Well-Architected incident management practice | SOURCE-ANALYSED; the lifecycle diagram is a teaching synthesis, not the live process of an organization |
| AZ06-02 §02, Fig 18-2 | Metrics, logs and distributed traces offer different views; Activity Log, resource logs and application telemetry have different scopes and availability; event time and ingest/arrival time should be recorded separately | Azure Monitor data platform; Activity Log; Resource Logs; diagnostic settings; ingestion time | SOURCE-ANALYSED; no live workspace, diagnostic setting, schema, event or ingestion delay was inspected |
| AZ06-02 §02–03 | Resource Logs are not collected by default and require diagnostic settings; missing data can reflect collection, schema, time-window or trace-correlation gaps and must remain unknown | Resource Logs; diagnostic settings; Application Insights telemetry model | SOURCE-ANALYSED; the fixture includes complete synthetic observations and does not model sampling or Azure ingestion |
| AZ06-02 §03, Fig 18-3 | Request/dependency operation and parent identifiers can correlate one distributed operation; Service Health and Resource Health have different scopes, and a healthy resource snapshot does not prove the application works | Application Insights telemetry data model; Azure Service Health FAQ; Azure Resource Health FAQ | SOURCE-ANALYSED; the chapter records the synthetic snapshot as “not observed, not excluded” |
| AZ06-02 §04, Fig 18-4 | The bank case separates release trigger, identity/authorization failure mechanism, payment impact and missing release-readiness control; only a controlled same-request repair/retest supports this synthetic causal explanation | Incident management investigation guidance; Azure role assignments; Blob data access role scope | DESIGN + LOCAL_VERIFIED; root cause applies to the fixture only, not an Azure workload |
| AZ06-02 §05, Fig 18-5 | Blob data roles can be scoped to a container; bounded access, approval, an original business probe, ledger/idempotency checks, negative access tests and stability form the local repair contract | Assign Azure role for Blob data access; Azure RBAC role assignments; incident management validation guidance | SOURCE-ANALYSED + LOCALLY SPECIFIED; no role assignment or storage request was made; real role propagation was not tested |
| AZ06-02 §06–07 | One deterministic synthetic banking incident and 30 tests exercise evidence time, competing hypotheses, authorization scope, same-probe recovery, ledger integrity, idempotency, stability and RTO; the chapter maps IR-01…IR-12 but does not pass the eight mandatory incident contracts | `chapters/AZ06-02/labs/incident-model`; `AZURE_SPECIALTY_ROADMAP.md`; `textbook/LIVE_LAB_INDEX.md` | LOCAL_VERIFIED 2026-11-27; Windows and WSL suites each passed 310 tests across 18 lab directories; no Azure/KQL/service emulation |
| AZ06-02 cost / authorization | No Azure sign-in, telemetry query, identity/role action, deployment, network probe, resource operation or billing request was performed | Session and command execution record | LIVE_NOT_RUN; actual cumulative spend remains NOT_VERIFIED |

### AZ06-02 primary references

- https://learn.microsoft.com/en-us/azure/well-architected/design-guides/incident-management
- https://learn.microsoft.com/en-us/azure/azure-monitor/fundamentals/data-platform
- https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-ingestion-time
- https://learn.microsoft.com/en-us/azure/azure-monitor/fundamentals/activity-log
- https://learn.microsoft.com/en-us/azure/azure-monitor/logs/resource-logs
- https://learn.microsoft.com/en-us/azure/azure-monitor/platform/diagnostic-settings
- https://learn.microsoft.com/en-us/azure/azure-monitor/app/data-model-request-telemetry
- https://learn.microsoft.com/en-us/azure/service-health/service-health-faq
- https://learn.microsoft.com/en-us/azure/service-health/resource-health-faq
- https://learn.microsoft.com/en-us/azure/storage/blobs/assign-azure-role-data-access
- https://learn.microsoft.com/en-us/azure/azure-monitor/change/change-analysis-enable
- https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments



## AZ07-01 — Terraform Core, Provider, graph, State, Plan and Import

Research date: 2026-11-27. HashiCorp Developer and the official Terraform Registry document Terraform behavior; Microsoft Learn documents AzureRM/AzAPI roles and migration guidance. The local Terraform CLI lab uses only the built-in terraform_data resource. The companion Python model is synthetic and deterministic.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ07-01 §01, Fig 19-1 | Terraform Core manages configuration, modules, dependency graph, State and Plan; a Terraform Provider plugin supplies resource schemas and service operations; Azure Resource Provider is an ARM namespace service | Terraform resource blocks; AzureRM/AzAPI choice; AzAPI Registry overview | SOURCE-ANALYSED; no plugin or Azure service was initialized |
| AZ07-01 §01 | AzureRM provides curated typed Azure resource schemas; AzAPI provides a thin ARM REST layer with explicit API version/body; one ARM object must not be managed from two Terraform addresses | AzureRM/AzAPI choice; official Azure/azapi Registry docs; Terraform state/address semantics | SOURCE-ANALYSED; no remote object or state was inspected |
| AZ07-01 §01, Fig 19-4 | Provider registration behavior is version-dependent. Current AzureRM 5.x documentation describes registration settings with a none default; earlier provider versions differed. Review the locked provider version and registration configuration before plan/apply | AzureRM 5.x Provider Registry docs and versioned upgrade guidance | SOURCE-ANALYSED; no AzureRM plugin was downloaded or configured; no registration request occurred |
| AZ07-01 §02 | Root and child modules declare provider requirements; the provider lock file fixes selected provider versions/checksums while remote module versions need their own constraints; child-module aliases must be passed explicitly | Provider requirements; dependency lock file; module block; providers within modules | SOURCE-ANALYSED; no external provider or module was initialized |
| AZ07-01 §02–03, Fig 19-2 | Resource/module references produce implicit graph dependencies; depends_on is for hidden dependencies; graph topology controls ordering/parallelism but does not prove Azure application readiness | Terraform dependency graph and references | SOURCE-ANALYSED; Python DAG tests cover a small synthetic graph only |
| AZ07-01 §04, Fig 19-3 | Terraform State binds a resource address to its provider-managed remote object, may include sensitive values, and requires safe collaboration/locking; a remote object should be managed at one address | Terraform State; state resource addressing; state locking | SOURCE-ANALYSED; no real State/backend was read or modified |
| AZ07-01 §05, Fig 19-4 | Plan compares configuration and prior state, normally refreshing remote observations; validate checks syntax/internal consistency only. Lifecycle rules affect replacement/destroy/drift visibility and are not approval controls | terraform plan; terraform validate; lifecycle meta-arguments | SOURCE-ANALYSED; no Azure plan, provider registration, apply or destroy was run |
| AZ07-01 §06 | Import requires a configured destination resource and provider-specific ID; review import and subsequent configuration drift before apply. Provider-type migration must use documented state guidance and inspect for recreation | Import blocks; AzureRM/AzAPI migration path; module refactoring; state mv | SOURCE-ANALYSED; import examples were not executed |
| AZ07-01 §07, labs/terraform-core | Terraform 1.15.5 Windows CLI initialized the local child module with built-in terraform.io/builtin/terraform; validate passed; three terraform test plan runs passed, including expected failures for invalid environment/scope | terraform_data; Terraform test framework; local lab files | LOCAL_VERIFIED 2026-11-27; no AzureRM/AzAPI provider, backend, credential, ARM ID, apply or cloud call |
| AZ07-01 §07, labs/core-model | 26 standard-library unit tests cover deterministic DAG ordering/cycles, synthetic AzureRM/AzAPI provider choice, unique address/object bindings, simplified lifecycle classification and import contracts | chapters/AZ07-01/labs/core-model | LOCAL_VERIFIED 2026-11-27 on Windows and WSL; model is not Terraform Core, provider, Azure API, real state, or cloud-plan emulation |
| AZ07-01 suite | Full Python suites passed 336 tests across 19 lab directories on Windows and in WSL; terraform fmt -check -recursive -diff textbook/chapters passed; the new local Terraform root passed init/validate/test on Windows | Project test runner; Terraform CLI output | LOCAL_VERIFIED 2026-11-27; WSL does not have Terraform CLI, so Terraform CLI checks were not run there |
| AZ07-01 cost / authorization | No Azure authentication, Azure/ARM/Entra query, Azure provider initialization/registration, resource mutation, live plan/import, network probe or billing request was performed | Session and command execution record | LIVE_NOT_RUN; this chapter's local execution made no Azure request or project Azure resource charge; cumulative actual spend remains NOT_VERIFIED |

### AZ07-01 primary references

- https://learn.microsoft.com/en-us/azure/developer/terraform/azurerm/overview-azapi-provider
- https://registry.terraform.io/providers/Azure/azapi/latest/docs
- https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/index
- https://learn.microsoft.com/en-us/azure/developer/terraform/how-to-migrate-between-azurerm-and-azapi
- https://developer.hashicorp.com/terraform/language/providers/requirements
- https://developer.hashicorp.com/terraform/language/files/dependency-lock
- https://developer.hashicorp.com/terraform/language/block/module
- https://developer.hashicorp.com/terraform/language/modules/develop/providers
- https://developer.hashicorp.com/terraform/language/modules/configuration
- https://developer.hashicorp.com/terraform/cli/state/resource-addressing
- https://developer.hashicorp.com/terraform/internals/graph
- https://developer.hashicorp.com/terraform/language/expressions/references
- https://developer.hashicorp.com/terraform/language/state
- https://developer.hashicorp.com/terraform/language/state/locking
- https://developer.hashicorp.com/terraform/cli/commands/plan
- https://developer.hashicorp.com/terraform/cli/commands/validate
- https://developer.hashicorp.com/terraform/cli/commands/init
- https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle
- https://developer.hashicorp.com/terraform/language/block/import
- https://developer.hashicorp.com/terraform/language/import/single-resource
- https://developer.hashicorp.com/terraform/language/modules/develop/refactoring
- https://developer.hashicorp.com/terraform/cli/state/mv
- https://developer.hashicorp.com/terraform/language/resources/terraform-data
- https://developer.hashicorp.com/terraform/language/tests

## AZ07-02 — Azure Remote State, locking and drift

Research date: 2026-11-27. HashiCorp Developer documents Terraform backend, lock, state, CLI and recovery behavior; Microsoft Learn documents Blob RBAC, versioning and soft-delete behavior. The local lab uses Windows Terraform CLI with the pinned `hashicorp/local` v2.9.1 provider and a local State/file only.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ07-02 §01, Fig 20-1 | AzureRM backend stores State in the selected Blob key; backend credentials must access the Blob data plane; Entra Storage Blob Data Contributor is scoped to the container; ordinary ARM Contributor alone does not grant Blob data access | AzureRM backend docs; Microsoft Storage built-in roles; Blob authorization with Entra ID | SOURCE-ANALYSED; no backend, principal, role or Azure endpoint was configured or queried |
| AZ07-02 §01 | Backend blocks cannot reference Terraform variables/resources; `.terraform/` may contain initialized backend configuration; `-backend-config` values must be handled as sensitive where appropriate | Terraform backend configuration docs; `terraform init` | SOURCE-ANALYSED; no credential or backend configuration was used |
| AZ07-02 §02, Fig 20-2 | Terraform locks state for operations that could write when the backend supports it; AzureRM uses Blob leases; the lock protects one key, not distinct keys or duplicate management of an Azure object; `force-unlock` needs the matching lock ID and must not break an active writer | AzureRM backend; state locking; force-unlock | SOURCE-ANALYSED; no Azure Blob lease was acquired or released |
| AZ07-02 §03, Fig 20-3 | Bootstrap the account/container outside the backend it enables; `init -migrate-state` attempts to migrate existing State while `-reconfigure` disregards old backend config; key and container scopes define different isolation boundaries | Terraform backend and init docs; Microsoft Blob RBAC scope docs | SOURCE-ANALYSED; no remote migration or Azure scope was used |
| AZ07-02 §04, Fig 20-4 | Normal plan refreshes observable objects and compares against configuration; refresh-only proposes State changes and does not change the remote object; intentional drift requires updating HCL and reviewing a new plan | `terraform plan` docs | SOURCE-ANALYSED; AzureRM drift was not executed |
| AZ07-02 §04, labs/terraform-state | With Terraform v1.15.5 and local provider v2.9.1, editing the managed file yielded exit code 2 and a `+ create` plan; refresh-only removed the local_file binding while leaving the modified file; normal apply recreated the declared content | `labs/terraform-state/scripts/verify_lab.py`; local provider `local_file` schema docs | LOCAL_VERIFIED 2026-11-27; specific to this provider resource/version, not an AzureRM drift claim |
| AZ07-02 §05, Fig 20-5 | Blob versioning retains versions on writes but incurs storage; versioning cannot restore deleted accounts/containers; state push has lineage/serial protections that `-force` bypasses | Microsoft Blob versioning/soft-delete docs; Terraform state and state-push docs | SOURCE-ANALYSED; no Blob version or Azure State recovery was performed |
| AZ07-02 §06, labs/terraform-state | An actual Terraform apply held the Windows local state backend operation open; a second CLI `plan -lock-timeout=0s` against the same state returned `Error acquiring the state lock`; local backend diagnostic reported an OS file-lock conflict | `scripts/hold_state_lock.py`, `scripts/release_state_lock.py`, `scripts/verify_lab.py`; actual CLI transcript in ignored `work/verification.log` | LOCAL_VERIFIED 2026-11-27; Windows local file locking is not Azure Blob lease evidence |
| AZ07-02 §06, State recovery | `state pull` captured lineage/serial; after moving the state file, `state list` reported no file; `state push` restored `local_file.marker`; next plan returned no changes; destroy removed the local resource | `scripts/verify_lab.py`; Terraform state-backend/state-push docs | LOCAL_VERIFIED 2026-11-27; local state only, no cloud resource restore |
| AZ07-02 suite | Windows `terraform init -backend=false`, validate, two local plan tests and repository-wide fmt check passed; full Python suites on Windows and WSL each passed 336 tests across 19 lab directories | Terraform CLI output; `textbook/tools/test_all.sh --python`; full project runner | LOCAL_VERIFIED 2026-11-27; WSL has no Terraform CLI |
| AZ07-02 cost / authorization | No Azure authentication, subscription/ARM/Entra query, Azure provider/backend initialization, Storage request, network probe, mutation or billing request occurred | Session and command execution record | LIVE_NOT_RUN; no project Azure charge from local execution; actual cumulative spend remains NOT_VERIFIED |

### AZ07-02 primary references

- https://developer.hashicorp.com/terraform/language/backend/azurerm
- https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/storage
- https://learn.microsoft.com/en-us/azure/storage/blobs/authorize-access-azure-active-directory
- https://developer.hashicorp.com/terraform/language/backend
- https://developer.hashicorp.com/terraform/cli/commands/init
- https://developer.hashicorp.com/terraform/language/state/locking
- https://developer.hashicorp.com/terraform/cli/commands/force-unlock
- https://developer.hashicorp.com/terraform/cli/state/recover
- https://developer.hashicorp.com/terraform/cli/commands/state/push
- https://developer.hashicorp.com/terraform/language/state/backends
- https://developer.hashicorp.com/terraform/cli/commands/plan
- https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file
- https://learn.microsoft.com/en-us/azure/storage/blobs/versioning-overview
- https://learn.microsoft.com/en-us/azure/storage/blobs/soft-delete-blob-overview
- https://developer.hashicorp.com/terraform/language/state

## AZ07-03 — Azure DevOps Pipelines and Workload Identity Federation

Research date: 2026-11-27. Azure DevOps and Microsoft Entra service behavior is source-analysed from Microsoft Learn; Terraform WIF variable names and backend/provider differences are cross-checked against current HashiCorp Registry/Developer documentation. The local pipeline YAML intentionally performs only offline unit tests.

| Chapter section / figure | Claim or teaching point | Source anchor | Classification and limit |
|---|---|---|---|
| AZ07-03 §01, Fig 21-1 | Stages contain jobs; jobs run on agents; files across jobs require explicit artifact transfer; Microsoft-hosted jobs use fresh VMs, while self-hosted cleanup depends on configuration | Azure Pipelines stages, artifacts and hosted-agent docs | SOURCE-ANALYSED; no Azure Pipeline job was run |
| AZ07-03 §02, Fig 21-2 | Azure Repos Git PR validation is configured as a target branch Build validation policy; YAML trigger governs push CI; branch policies and resource checks are separate gates | Azure Repos Git build docs; branch-policy docs; approvals/checks docs | SOURCE-ANALYSED; no Azure DevOps repository/policy was accessed |
| AZ07-03 §02 | Include templates reuse steps; extends templates can constrain schema; trust depends on protecting the template source and version | Azure Pipelines YAML templates docs | SOURCE-ANALYSED; no server-side template compilation or Required template check was performed |
| AZ07-03 §03, Fig 21-3 | Workload identity federation binds pipeline issuer/subject/audience to an Entra federated credential; successful exchange does not assign Azure resource permissions | Microsoft workload-identity service-connection docs; Azure RBAC concepts | SOURCE-ANALYSED; no Entra token, FIC, Service Connection or role was created or queried |
| AZ07-03 §03 | AzureRM provider and AzureRM backend have distinct Azure DevOps Service Connection ID environment variable names for OIDC; their State data access and resource-management permissions are separate decisions | HashiCorp AzureRM OIDC guide and AzureRM backend docs | SOURCE-ANALYSED; no AzureRM provider/backend was initialized |
| AZ07-03 §03, dated note | New WIF Service Connections default to Microsoft Entra issuer; a subset of legacy Azure DevOps issuer connections is scheduled to retire 2027-07-01 | Microsoft workload-identity service-connection docs, accessed 2026-11-27 | SOURCE-ANALYSED as of research date; announcement applies only to specified eligible public-cloud single-tenant connections; recheck before migration |
| AZ07-03 §03–05 | Service Connections cannot be substituted by YAML variables; secret Variable Groups need explicit Pipeline authorization; approvals/checks are configured by protected-resource owners outside YAML | Azure Pipelines service-connection, variable-group and approvals/checks docs | SOURCE-ANALYSED; no service resource or permission was configured |
| AZ07-03 §04, Fig 21-4 | A controlled saved Plan should bind source commit, target scope, provider lock, plan bytes, run, approver and expiry; stale or changed plans need a new review | Terraform plan/apply docs; Azure Pipelines artifact and approval mechanisms | DESIGN_GUIDANCE; no real cloud Plan or approval occurred |
| AZ07-03 §06, labs/azure-pipelines | Generic YAML parsing and local structural contracts verify the actual YAML/template text; PyYAML is not an Azure Pipelines schema compiler | `azure-pipelines.yml`, `templates/offline-checks.yml`, `tests/test_pipeline_yaml.py` | LOCAL_VERIFIED 2026-11-27; no server upload, queue, compile or service config |
| AZ07-03 §06, labs/azure-pipelines | Plan digest, source/target, lock-file digest, run and validity checks; 1 synthetic valid case and 11 fail-closed negative cases | `scripts/plan_gate.py`, `tests/test_plan_gate.py`; synthetic bytes and temporary JSON only | LOCAL_VERIFIED 2026-11-27; verifier does not authenticate an approver, parse a Terraform plan, or call Azure |
| AZ07-03 suite | Full Python suite passed 353 tests across 20 lab directories on Windows and WSL | `textbook/tools/test_all.sh --python` and local test output | LOCAL_VERIFIED 2026-11-27; not Azure DevOps execution |
| AZ07-03 cost / authorization | No Entra token, Azure credential, Azure DevOps organization, Azure query, resource operation or billing request occurred | Session and command execution record | LIVE_NOT_RUN; no project Azure request or charge from local execution; cumulative actual spend remains NOT_VERIFIED |

### AZ07-03 primary references

- https://learn.microsoft.com/en-us/azure/devops/pipelines/process/stages?tabs=yaml&view=azure-devops
- https://learn.microsoft.com/en-us/azure/devops/pipelines/process/templates?view=azure-devops
- https://learn.microsoft.com/en-us/azure/devops/pipelines/repos/azure-repos-git?view=azure-devops
- https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops
- https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/hosted
- https://learn.microsoft.com/en-us/azure/devops/pipelines/artifacts/pipeline-artifacts?tabs=yaml-task&view=azure-devops
- https://learn.microsoft.com/en-us/azure/devops/pipelines/release/configure-workload-identity?view=azure-devops
- https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/deploy/azure-cli
- https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops
- https://learn.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops
- https://learn.microsoft.com/en-us/azure/devops/pipelines/process/environments?view=azure-devops
- https://learn.microsoft.com/en-us/azure/devops/pipelines/policies/retention?view=azure-devops
- https://learn.microsoft.com/en-us/azure/devops/pipelines/yaml-schema?view=vsts
- https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/guides/service_principal_oidc
- https://developer.hashicorp.com/terraform/language/backend/azurerm
- https://developer.hashicorp.com/terraform/cli/commands/plan
- https://developer.hashicorp.com/terraform/language/state/locking
- https://learn.microsoft.com/en-us/azure/role-based-access-control/scope-overview
