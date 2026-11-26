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