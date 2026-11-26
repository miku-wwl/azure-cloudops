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
