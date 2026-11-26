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
