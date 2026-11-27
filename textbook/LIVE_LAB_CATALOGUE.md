# E9 live-lab catalogue

- **Prepared:** 2026-11-26 (Pacific/Auckland)
- **Stage:** L0 read-only preflight complete; all Azure incident execution remains NOT_RUN. No mutation is authorized by this catalogue.
- **Cumulative Azure ceiling:** USD 1.00 gross; plan below USD 0.70 and retain USD 0.30 for delayed charges and cleanup. No estimate below is deployment approval.
- **Scope rule:** Use only a dedicated, specifically authorized lab scope. L0 findings and limits are recorded below. Stage 2 and Stage 3 L0 made no Azure resource changes.

Each card contains the required E9 fields. “Not established” marks a stop condition: any remaining account, quota, SKU, dependency, price, runtime or teardown gap must be resolved before mutation. Maximum lifetime includes diagnosis, recovery, teardown and a residual-resource check.

## L0 observed outcome — 2026-11-26 (read-only)

The existing Azure CLI context was Enabled in AzureCloud and remained the default. The current-principal assignment query returned two subscription-scope records with Owner as the unique role; this does not evaluate group-derived access or grant this project approval. One resource group and three listable resources were visible, all Microsoft.Network/networkWatchers; all three Network Watchers reported Succeeded. No project lab network or App Service was present in the listable inventory. Microsoft.Web and Microsoft.Insights were Registered; no provider was registered during this preflight. Australia East is supported by the subscription; the Linux F1 location query returned Australia East; and the Linux runtime list included NODE:24-lts. An earlier 0/2 response was interpreted as an F1 instance quota, but the official Microsoft.Web regional usage API contract defines core usage. The initial F1 plan inventory was not verified; a later 2026-11-27 read-only recheck found 0 visible F1/Free plans in Australia East, while account entitlement and regional capacity remain NOT_VERIFIED. The earlier correction itself made no Azure request; details of the subsequent recheck are in the dated section below. The proposed resource-group name was absent and the candidate App Service site name was available when checked. These checks do not guarantee later availability or capacity.

Two Cost Management Usage queries returned HTTP 429. No actual billing value was obtained; actual spend remains NOT_VERIFIED. Raw subscription, tenant, principal and resource identifiers were redacted and not retained. See [L0_READ_ONLY_PREFLIGHT.md](L0_READ_ONLY_PREFLIGHT.md) for the exact evidence and limitations.

## LAB-IR-11 read-only recheck — 2026-11-27

The existing default CLI context remained Enabled. A current subscription-wide App Service plan listing returned 0 visible F1/Free plans in Australia East; the dedicated resource group was absent, `NODE:24-lts` and Linux F1 in Australia East were listed, and the candidate site name check returned available. The inline JSON name-check request failed with an empty-body HTTP 400; the same read-only check succeeded using a temporary file body. The guarded runbook now uses that file-based form and removes it. Account offer entitlement, live deployment capacity and actual billing remain NOT_VERIFIED. Repeat the checks immediately before any authorized write.

## Candidate A governance reads — 2026-11-27

Subscription-scoped reads returned 996 role definitions, 3,760 policy definitions (2,928 BuiltIn and 832 Static), and 2 policy assignments. The seven-day Activity Log query returned 10 Administrative events, which is the request's sample cap. No event details or identifiers were retained. The management-group list was unavailable with provider auto-registration disabled. Microsoft.ResourceGraph was Registered, but the CLI extension was not installed and no Resource Graph data query ran. No provider registration, resource write, sign-in or context switch occurred. See L0_READ_ONLY_PREFLIGHT.md for limits.

## L0 subscription and CLI recheck — 2026-11-28

A direct read-only subscription GET returned `AzureForStudents_2018-01-01` with `spendingLimit=On`; that credit control is not the project's USD 1.00 ceiling. The current plan inventory showed 0 visible F1 plans in Australia East, while the F1 location list still included Australia East. Resource Graph extension installation failed locally because pip could not load Azure CLI's bundled Python `pyexpat`; the explicit-subscription REST fallback returned 3 `microsoft.network/networkwatchers` records without truncation. A fresh candidate recheck confirmed the dedicated group was absent, `NODE:24-lts` and Linux F1 in Australia East were listed, and the candidate app name was available. Microsoft's [Azure for Students offer](https://azure.microsoft.com/en-us/free/students) includes an always-free App Service allocation, supporting the conditional USD 0.00 estimate; account-specific provisioning eligibility and regional capacity remain NOT_VERIFIED. No Azure resource mutation occurred. Actual billing remains NOT_VERIFIED. The owner also directed that the interactive KQL demo sign-in be skipped; its seven templates remain NOT_RUN. See L0_READ_ONLY_PREFLIGHT.md.

## LAB-L0-01 — Read-only account and scope preflight

| Field | Plan |
|---|---|
| Lab ID | `LAB-L0-01` |
| Associated lecture | AZ00-01, AZ05-03, FIN-01 |
| Associated incident IDs | IR-01–IR-12 (scope and prerequisites only) |
| Deployment architecture | Use only the already-authenticated Azure CLI context; inspect the current account, explicitly named subscription/RG scope, existing resources, effective read permissions, provider registration, quota/SKU/region availability, and available pricing/billing evidence. Never log in, switch the default subscription, or emit raw identifiers. |
| Required permissions | Current session; read-only `Reader` at the specifically approved scope; `Resource Graph Reader` only if needed there; narrowly scoped cost/billing read permission only if authorized. |
| Region and SKU | Not applicable; inventory only. |
| Terraform root module | None. |
| Resource list | None created or modified. |
| Estimated cost | USD 0 incremental resource cost. Azure documents Resource Graph as a free service; this does not verify prior subscription spend or downstream tool/egress charges. |
| Maximum lifetime | 30 minutes; no resource lifetime. |
| Baseline probes | `az account show` (redacted immediately), then explicit-scope read-only inventory and access checks only after confirming the current session and scope. |
| Fault injection | None. |
| Diagnostics | Classify missing session, wrong scope, authorization gaps, unregistered provider, unavailable SKU/quota, inaccessible cost data, and incomplete/partial inventory separately. |
| Recovery | Stop on an unknown identity or scope; preserve the default context; ask the owner for a specific read grant or scope decision. |
| Teardown | None. |
| Residual-resource checks | Confirm the query created no resources and did not alter account context. |
| Delayed billing checks | Record actual spend as `NOT_VERIFIED` unless billing evidence explicitly establishes it; do not infer USD 0 from a missing cost view. |
| Classification | **Zero-cost read-only** |

## LAB-IR-01 — Private DNS resolution

| Field | Plan |
|---|---|
| Lab ID | `LAB-IR-01` |
| Associated lecture | AZ02-03; integrated diagnosis AZ06-02 |
| Associated incident IDs | IR-01 |
| Deployment architecture | Prefer a read of an already-authorized lab private DNS zone and endpoint. A fault/recovery drill would need an isolated lab VNet, private endpoint and lab-only zone/link, with one synthetic name. |
| Required permissions | Exact-scope network and DNS reads; `Private DNS Zone Contributor` and narrowly scoped network write only under separate approval. |
| Region and SKU | Exact approved region and supported target SKU TBD at L0; the zone itself is global. |
| Terraform root module | `textbook/terraform/azure-enterprise-reference/` and `modules/private_endpoint/` contain reusable PE/private-DNS pieces; no reviewed incident-specific root and target fixture are ready. |
| Resource list | Lab VNet/subnet, private DNS zone/link, private endpoint to an approved synthetic target, and test endpoint if none already exists. |
| Estimated cost | **Not established; budget-deferred.** Private endpoint hours/traffic and DNS-zone/queries plus target compute/storage must be priced for the chosen region and actual duration. |
| Maximum lifetime | 45 minutes for the lab resources; remove in the same approved run. |
| Baseline probes | Query the explicit lab resolver for one lab FQDN; compare expected private address; call the same synthetic HTTP endpoint. |
| Fault injection | Remove or corrupt exactly one lab record; never change a shared zone, resolver, host DNS, public DNS, or production endpoint. |
| Diagnostics | DNS response/TTL, linked VNet, PE connection/state, effective client resolver, and same-path TCP/HTTP probe. |
| Recovery | Restore the exact record and repeat the identical DNS and application probes. |
| Teardown | Delete only lab-owned records/link/endpoint/zone/VNet resources in dependency order. |
| Residual-resource checks | Enumerate the lab RG and DNS links; verify no PE, NIC, IP configuration, zone link, or record remains. |
| Delayed billing checks | Review endpoint-hours, traffic, DNS queries and target dependencies after meter delay; retain contingency until reconciled. |
| Classification | **Budget-deferred** |

## LAB-IR-02 — NSG flow denial

| Field | Plan |
|---|---|
| Lab ID | `LAB-IR-02` |
| Associated lecture | AZ02-02, AZ02-04; integrated diagnosis AZ06-02 |
| Associated incident IDs | IR-02 |
| Deployment architecture | Use only an isolated, already-running lab NIC/subnet and two lab-only TCP probes. Prefer a configuration-only NSG change; do not create a VM solely to probe. |
| Required permissions | `Network Reader`/effective-security-rule read at the named NIC; exact NSG write role at the lab resource group only after approval. |
| Region and SKU | Reuse the approved lab network's actual region and existing NIC/NSG; no new SKU assumed. |
| Terraform root module | No NSG rule resource or incident root exists. `azure-enterprise-reference/modules/network/` creates VNet/subnets only. |
| Resource list | Existing lab NIC, subnet and NSG; one temporary priority rule; no new resource in the preferred path. |
| Estimated cost | **Potentially USD 0 incremental resource cost only on existing lab infrastructure.** Probes/monitoring dependencies and any needed compute must be costed; not yet verified. |
| Maximum lifetime | 15 minutes; remove the temporary rule immediately after recovery. |
| Baseline probes | Confirm one allowed tuple passes and one negative-control tuple is blocked; record effective NSG rule and route. |
| Fault injection | Add one deny rule for one exact source/destination/protocol/port; never broaden an allow rule or touch shared traffic. |
| Diagnostics | Effective security rules, rule priority and match, NIC/subnet NSG association, route, listener state, and both tuple probes. |
| Recovery | Delete the one lab-owned deny rule; repeat the blocked tuple probe and preserve the negative-control result. |
| Teardown | Restore captured pre-run NSG state and delete only the temporary rule. |
| Residual-resource checks | Re-read the exact NSG and effective rules; compare to the captured baseline and ensure no temporary rule remains. |
| Delayed billing checks | No new metered service is planned; inspect cost data after the normal delay if any supporting service was used. |
| Classification | **Potentially zero-cost live mutation** |

## LAB-IR-03 — UDR next-hop error

| Field | Plan |
|---|---|
| Lab ID | `LAB-IR-03` |
| Associated lecture | AZ02-01; integrated diagnosis AZ06-02 |
| Associated incident IDs | IR-03 |
| Deployment architecture | Use an existing isolated lab subnet and endpoint, and one exact test prefix. No gateway, NVA, hub, peering, or default route. |
| Required permissions | Exact NIC/route-table read; Network Contributor on the lab route table only for an explicitly approved change. |
| Region and SKU | Reuse actual lab region and existing endpoint; no new compute/SKU assumed. |
| Terraform root module | No route-table/UDR resource or incident root exists. The network module creates only VNet and subnets. |
| Resource list | Existing lab route table, subnet association and test NIC; one temporary route entry. |
| Estimated cost | **Potentially USD 0 incremental resource cost on existing lab resources.** Any new endpoint, NVA/gateway or billed probe makes the estimate unestablished and blocks this path. |
| Maximum lifetime | 15 minutes; restore before ending the run. |
| Baseline probes | Read configured and effective routes for the lab NIC and confirm the exact test prefix reaches the expected next hop. |
| Fault injection | Change or remove only one approved test-prefix route; never change `0.0.0.0/0` or a shared route. |
| Diagnostics | Longest-prefix selection, effective routes, route association, next-hop type/address, NSG and same destination probe. |
| Recovery | Restore the captured route and repeat the route read plus identical probe. |
| Teardown | Restore the exact pre-run route-table configuration. |
| Residual-resource checks | Compare configured/effective routes against pre-run capture; verify no temporary route or association remains. |
| Delayed billing checks | No new metered resource is planned; check only if probe or diagnostic services introduce billable usage. |
| Classification | **Potentially zero-cost live mutation** |

## LAB-IR-04 — VNet peering path failure

| Field | Plan |
|---|---|
| Lab ID | `LAB-IR-04` |
| Associated lecture | AZ08-01; integrated diagnosis AZ06-02 |
| Associated incident IDs | IR-04 |
| Deployment architecture | Two disposable, non-overlapping lab VNets with reciprocal peerings and isolated test endpoints; no transit, gateway, Route Server, NVA, VPN or production adjacency. |
| Required permissions | Exact VNet/peering/route reads and write on both lab VNets, approved explicitly for the same run. |
| Region and SKU | Actual approved regions TBD; peering regions, address spaces and any endpoint SKU must be validated at L0. |
| Terraform root module | No VNet-peering root or Terraform resource exists. |
| Resource list | Two VNets, two peering objects, endpoint(s) if not already present, and test traffic. |
| Estimated cost | **Not established; budget-deferred.** Peering traffic, endpoints and cross-region transfer may be billed; no safe numeric gross estimate exists yet. |
| Maximum lifetime | 30 minutes including restore/delete. |
| Baseline probes | Read both peer states/address spaces/forwarding flags and run one approved lab path probe. |
| Fault injection | Change one side's lab peering state or a paired lab-only flag; never affect a shared hub/spoke. |
| Diagnostics | Both peering objects, effective routes, paired forwarding/gateway flags, NSGs and the same path probe. |
| Recovery | Restore the paired setting and verify connected state, routes and identical probe. |
| Teardown | Delete only lab-owned peerings and VNets/endpoints, if created. |
| Residual-resource checks | Enumerate both VNets, peering objects, NICs, public IPs and dependent diagnostic resources. |
| Delayed billing checks | Reconcile peering data transfer and any regional endpoint/compute meters after billing delay. |
| Classification | **Budget-deferred** |

## LAB-IR-05 — Managed identity and data authorization

| Field | Plan |
|---|---|
| Lab ID | `LAB-IR-05` |
| Associated lecture | AZ03-01, AZ03-02, AZ04-04; integrated diagnosis AZ06-02 |
| Associated incident IDs | IR-05 |
| Deployment architecture | Read existing lab identity and role assignments; a live test requires one approved workload identity and one synthetic object/container with a narrowly scoped data-plane role. |
| Required permissions | Exact identity/role reads; role assignment write only through a separately authorized principal with scope limited to the test object/container. |
| Region and SKU | Reuse the workload's approved region and actual supported identity/Storage resource; no new SKU assumed. |
| Terraform root module | The enterprise reference contains user-assigned identity and Storage modules; it has no incident-specific workload or narrowly tested data-role root. |
| Resource list | Existing lab workload/identity and synthetic object; optional user-assigned identity, Storage account/container and role assignment only if explicitly approved. |
| Estimated cost | **Not established.** Compute/Storage dependency and data operations must be estimated; role assignment alone is not a complete cost model. |
| Maximum lifetime | 30 minutes; revoke only the run-owned grant in the approved teardown. |
| Baseline probes | Same principal reads one allowed object, cannot write it, and cannot read an out-of-scope object; record claims without tokens/secrets. |
| Fault injection | Remove only the exact lab data read grant or test a wrong audience in an isolated request; do not alter a shared identity. |
| Diagnostics | Principal/object/scope, authentication result, token audience/claims from approved in-memory handling, data-plane response, and negative controls. |
| Recovery | Restore the minimal data role or correct the lab request; repeat the same read/digest and retain write/out-of-scope denials. |
| Teardown | Remove only the test role assignment and synthetic object/identity resources owned by the run. |
| Residual-resource checks | Re-read role assignments and identity attachments; confirm no grant or credential remains and no unrelated assignment changed. |
| Delayed billing checks | Review any Storage/compute usage after meter delay; do not expose tokens or values to billing evidence. |
| Classification | **Permission-deferred** |

## LAB-IR-06 — Key Vault access boundary

| Field | Plan |
|---|---|
| Lab ID | `LAB-IR-06` |
| Associated lecture | AZ03-02, AZ04-04; integrated diagnosis AZ06-02 |
| Associated incident IDs | IR-06 |
| Deployment architecture | Read an approved vault's network/RBAC metadata; a fault test needs a dedicated vault, workload identity, synthetic secret and possibly private endpoint/DNS. Never use production secrets. |
| Required permissions | Vault/network/role read; one approved secret operation; explicit vault/network/RBAC writes for any fault and teardown. |
| Region and SKU | Exact region and Standard/Premium tier must be decided from approved scope; no tier assumed. |
| Terraform root module | `azure-enterprise-reference/` has Key Vault, identity, network and private-endpoint modules; current purge protection/soft delete leaves a retained object after destroy. |
| Resource list | Vault, one synthetic secret, identity/workload, optional PE/private DNS/VNet, plus any probe host. |
| Estimated cost | **Not established; budget-deferred.** Operations, tier, PE-hours, networking, DNS and retained soft-deleted vault lifetime all require current pricing and cleanup review. |
| Maximum lifetime | 30 minutes of active use; retained soft-delete interval may exceed this and must be costed before selection. |
| Baseline probes | One approved data-plane request; verify only status/metadata and never print secret values. |
| Fault injection | Inject exactly one condition: scoped data permission, audience, or lab network path. |
| Diagnostics | DNS/TCP/TLS, principal/audience, exact data role/scope, vault network settings and non-secret secret metadata. |
| Recovery | Restore only the changed lab condition; repeat the same approved request and verify expected non-secret result/digest. |
| Teardown | Remove synthetic secret and only approved lab resources; purge-protection constraints must be resolved before deployment. |
| Residual-resource checks | Inspect vault, soft-deleted vault/secret state, PE, DNS, VNet and role assignments; any retained item blocks a zero-residual claim. |
| Delayed billing checks | Check vault operations, endpoint/traffic, DNS, and any retained soft-delete charges after their billing delay. |
| Classification | **Budget-deferred** |

## LAB-IR-07 — AKS/ACR image pull

| Field | Plan |
|---|---|
| Lab ID | `LAB-IR-07` |
| Associated lecture | AZ04-03, AZ03-02; integrated diagnosis AZ06-02 |
| Associated incident IDs | IR-07 |
| Deployment architecture | Prefer authorized reads of an existing disposable AKS/ACR pair. A live failure needs an isolated cluster/namespace and a run-owned test image/tag; no public registry. |
| Required permissions | Scoped AKS/ACR reads and Kubernetes namespace access; role/network repair requires a separately approved exact grant. |
| Region and SKU | AKS tier/node size/count, ACR tier, region, disks and networking TBD; all must be quoted before use. |
| Terraform root module | `azure-enterprise-reference/` includes AKS, ACR and identity modules, but provisions a private cluster, node resource group and networking; it is not a low-cost incident root. |
| Resource list | AKS control plane/node pool/node RG, ACR, identity/RBAC, VNet/subnet, load-balancer/egress, disks and image data. |
| Estimated cost | **Not established; budget-deferred.** Compute, disks, load balancing, ACR, networking and egress cannot be presumed free. |
| Maximum lifetime | At most 60 minutes, only if a complete provision/use/delete estimate fits the gross ceiling and node-RG residual contract. |
| Baseline probes | A known approved image reaches Ready and passes one application probe; verify registry identity/path without exposing credentials. |
| Fault injection | Use one nonexistent manifest/tag in the isolated namespace, or one explicit approved fault; no cluster-wide identity or network changes. |
| Diagnostics | Pod events/status, exact image reference, registry response class, kubelet/identity/RBAC and node connectivity evidence. |
| Recovery | Correct the exact image reference or approved lab condition; repeat the same readiness and application probes. |
| Teardown | Delete only run-owned workload/ACR/cluster resources and separately allowlisted AKS node resource group contents. |
| Residual-resource checks | Enumerate cluster, node RG, NICs, disks, load balancers, public IPs, ACR data and role assignments. |
| Delayed billing checks | Reconcile AKS/node, disk, LB, IP, ACR storage and egress meters; retain the USD 0.30 contingency. |
| Classification | **Budget-deferred** |

## LAB-IR-08 — Azure Blob State lock and drift

| Field | Plan |
|---|---|
| Lab ID | `LAB-IR-08` |
| Associated lecture | AZ07-02, AZ07-01; delivery context AZ07-03 |
| Associated incident IDs | IR-08 |
| Deployment architecture | Use a dedicated existing non-production Storage container only if its owner authorizes a synthetic, non-sensitive Terraform state. The E8 local backend evidence remains separate and does not prove Blob lease behavior. |
| Required permissions | Storage blob data read/write at the test container; exact Storage management reads; no account keys or shared-key fallback. |
| Region and SKU | Existing approved account's actual redundancy/performance/SKU; new account would require exact region and Standard LRS estimate. |
| Terraform root module | `textbook/terraform/azure-remote-state-backend/` is backend configuration only; no remote init or disposable Azure resource root exists. |
| Resource list | Existing/new Storage account, one private test container/blob, Terraform state/lease operations, and optional probe compute. |
| Estimated cost | **Not established; budget-deferred.** Storage capacity, transactions, replication, network path, diagnostics and any private endpoint must be costed. |
| Maximum lifetime | 30 minutes; no sensitive state; release lease and delete only run-owned state/container as authorized. |
| Baseline probes | Backend-free local checks first; in Azure, acquire/release an approved lease and verify state object version/digest without printing contents. |
| Fault injection | Compete two test operations for the same isolated Blob lease; separately change one synthetic resource only if it is already safely scoped. |
| Diagnostics | Lease holder/ID metadata, operation result, Blob version/ETag, exact Terraform root/backend and sanitized state metadata. |
| Recovery | Release the owned lease, reconcile only the test state, and confirm a no-change plan; do not force-unlock an unknown lease. |
| Teardown | Delete the run-owned container/state only after owner approval and verified backup; never delete the shared Storage account. |
| Residual-resource checks | Check lease state, blob/version/snapshot, container, diagnostic settings and leftover temporary resources. |
| Delayed billing checks | Check capacity, transactions, replication and diagnostic/transfer meters after the service's billing delay. |
| Classification | **Budget-deferred** |

## LAB-IR-09 — Azure Policy deployment denial

| Field | Plan |
|---|---|
| Lab ID | `LAB-IR-09` |
| Associated lecture | AZ03-03, AZ07-01; integrated diagnosis AZ06-02 |
| Associated incident IDs | IR-09 |
| Deployment architecture | Read existing assignment/compliance state first. A write drill must be limited to one dedicated lab RG and a built-in policy with a harmless, predictable deny effect. |
| Required permissions | Policy/resource reads; `Resource Policy Contributor` (or narrower confirmed role) at the lab RG only after explicit approval. |
| Region and SKU | Exact region and test resource type/SKU from an approved lab RG; no existing resource is assumed. |
| Terraform root module | Enterprise reference supports one audit-only AzAPI assignment; no reviewed deny-assignment plus disposable deployment root exists. |
| Resource list | Temporary RG-scoped assignment and one minimal disposable test resource; no subscription/tenant definition. |
| Estimated cost | **Not established.** Policy service may not be the cost driver; the tested resource and cleanup are unpriced, so the complete run is blocked pending L0. |
| Maximum lifetime | 30 minutes for assignment; assignment must be removed before resource cleanup. |
| Baseline probes | Evaluate the harmless test resource without policy and record its exact scope/type. |
| Fault injection | Apply one temporary RG-level deny assignment; attempt only the intended disposable lab deployment. |
| Diagnostics | Activity/Policy denial event, assignment definition/effect, evaluated scope, exact request and correlation ID. |
| Recovery | Remove the temporary assignment, then verify the same test deployment can proceed or leave the resource absent. |
| Teardown | Delete only the temporary assignment/definition created by the run and any test resource. |
| Residual-resource checks | Confirm no assignment/definition remains at RG or parent scope; confirm no denied/partial resource is left. |
| Delayed billing checks | Check any test resource's meters; do not infer a zero-cost run just because the policy assignment itself had no meter. |
| Classification | **Permission-deferred** |

## LAB-IR-10 — Azure Monitor alert and recovery

| Field | Plan |
|---|---|
| Lab ID | `LAB-IR-10` |
| Associated lecture | AZ05-01, AZ05-02; integrated diagnosis AZ06-02 |
| Associated incident IDs | IR-10 |
| Deployment architecture | Start with read-only existing platform metrics/Activity Log. A full alert drill requires a supported lab target, one temporary alert rule and a bounded signal; avoid Log Analytics ingestion unless explicitly costed. |
| Required permissions | Metrics/Activity Log/alert reads; scoped `Monitoring Contributor` and target write only after approval. |
| Region and SKU | Existing approved target's region/SKU; alert signal, evaluation frequency and action group availability TBD. |
| Terraform root module | The monitoring module creates a Log Analytics workspace only; no metric-alert or action-group lab root is ready. |
| Resource list | Existing target and metrics; optional alert rule/action group and generated signal; optional workspace/ingestion only if cost-approved. |
| Estimated cost | **Not established; budget-deferred.** Alert rules/actions, logs, ingestion, retention and target workload must be checked for the precise signal and SKU. |
| Maximum lifetime | 30 minutes including alert resolution and rule deletion. |
| Baseline probes | Read baseline metric and active alert state; use the same health/metric probe before and after the run. |
| Fault injection | Generate a bounded test signal only on the lab target; do not send notifications to people or inject load into a shared service. |
| Diagnostics | Metric namespace/dimensions, aggregation/window, rule state, fired/resolved timestamps, action path and Activity Log. |
| Recovery | Stop signal generation, verify healthy metric and resolved alert, and repeat the same probe. |
| Teardown | Remove only the temporary alert/action resources and optional lab telemetry. |
| Residual-resource checks | Enumerate alerts, action groups, diagnostic settings, workspace tables/retention and test signal processes. |
| Delayed billing checks | Reconcile alert-rule, action, ingestion, retention, query and target resource meters after billing delay. |
| Classification | **Budget-deferred** |

## LAB-IR-11 — App Service release rollback

| Field | Plan |
|---|---|
| Lab ID | `LAB-IR-11` |
| Associated lecture | AZ04-02, AZ07-03; integrated diagnosis AZ06-02 |
| Associated incident IDs | IR-11 |
| Deployment architecture | Candidate only: one disposable Linux App Service F1 plan and app in the dedicated scope below; built-in NODE:24-lts with no third-party dependencies; deploy a known-good ZIP, a deterministic HTTP 500 ZIP, then redeploy the exact same known-good ZIP. No deployment slot or production traffic. |
| Required permissions | Subscription-scope resourceGroups/write to create the approved dedicated group, plus Microsoft.Web/serverfarms/write and Microsoft.Web/sites read/write/deploy within that group. Current-principal Owner assignment was observed, but its conditions/effective access were not fully evaluated and it is not this project’s approval. Do not create role assignments or retain extra access. |
| Region and SKU | Australia East (australiaeast), Linux F1 only; runtime NODE:24-lts is listed. The 2026-11-28 read-only plan inventory returned 0 visible F1/Free plans in Australia East; Linux F1 and the candidate app name were available in the fresh read-only recheck. The Azure for Students public offer lists an always-free App Service allowance, but account-specific deployment eligibility and regional capacity remain NOT_VERIFIED. The runbook rechecks the documented regional Free-plan limit and stops at 10 existing plans; it also stops if the current offer, runtime, regional SKU or name is unavailable. |
| Candidate exact scope (not approved) | Australia East; Linux F1 plan asp-azure-cloudops-ir11-aue; site azcoir11aue261126; dedicated resource group rg-azure-cloudops-ir11-aue. The group was absent and site name was available at L0; repeat both checks immediately before provisioning. |
| Terraform root module | No App Service/Web App/plan root exists; use only the reviewed, explicit Azure CLI runbook in incidents/live_ir11/ after approval. |
| Resource list | Proposed dedicated resource group rg-azure-cloudops-ir11-aue; one Linux F1 plan asp-azure-cloudops-ir11-aue; one site azcoir11aue261126; three small ZIP deployments to the same test endpoint. No log workspace, Application Insights, Storage account, private endpoint, slot or production traffic. |
| Estimated cost | Conditional gross USD 0.00 for the 45-minute candidate: Microsoft's Linux pricing page checked 2026-11-28 lists F1 under the Free plan, the Azure for Students public offer lists an always-free App Service allowance, and Azure lists the first 100 GB/month of Internet egress as free. This assumes account-specific F1 eligibility and regional capacity, usage within the published 60 CPU minutes/day and 1 GB storage, probes within the free egress allowance, and no paid dependency. Reconfirm current terms at execution; stop if the estimate is unreliable or exceeds USD 0.70 cumulative. Actual Azure billing remains NOT_VERIFIED. |
| Maximum lifetime | 45 minutes from the first resource write. Main operation window: 20 minutes; independent cleanup starts after 25 minutes if the primary process has not verified teardown, monitors late resource creation, and reserves a final bounded verification window before the hard stop. |
| Baseline probes | Known-good version returns the expected status/body from the same HTTPS path. |
| Fault injection | Publish a deterministic test package that returns HTTP 500 to the isolated app; never route real users to it. |
| Diagnostics | Deployment ID/version, HTTP probe status/body and deployment history. Do not enable App Service log streaming, diagnostic settings or a log workspace. |
| Recovery | Redeploy the previous known-good package to the same app and repeat the identical HTTPS probe. |
| Teardown | Primary process uses a finally block; an independent watchdog remains active after the primary cleanup marker. Both paths delete only the dedicated group carrying this run's project and run-ID tags, then verify az group exists is false and a subscription-wide resource query finds no objects in that group. Any failed cleanup blocks all further incidents. |
| Residual-resource checks | Check app, plan, hostnames, storage/deployment artifacts, diagnostic settings and resource-group contents. |
| Delayed billing checks | Reconcile app-plan time, storage, log and network meters after billing delay; stop at any unexpected billable dependency. |
| Classification | **Potentially zero-cost live mutation** |
## LAB-IR-12 — Blob version restore

| Field | Plan |
|---|---|
| Lab ID | `LAB-IR-12` |
| Associated lecture | AZ06-01, AZ04-04; integrated diagnosis AZ06-02 |
| Associated incident IDs | IR-12 |
| Deployment architecture | Use a dedicated container with three synthetic objects, versioning/soft-delete enabled, manifest captured before the fault, and a separate restore destination. Do not overwrite a source object during recovery. |
| Required permissions | Blob data read/write for the single test container; narrowly scoped Storage configuration read/write if required; no account keys. |
| Region and SKU | Exact approved Storage region; Standard/Hot/LRS is a candidate only and must be confirmed against the target. |
| Terraform root module | The Storage module enables versioning and seven-day soft delete, but no isolated restore lab root or retention/purge cleanup plan exists. |
| Resource list | Storage account/container, three small objects, object versions/soft-deleted bytes, manifest and separate restore path. |
| Estimated cost | **Not established; budget-deferred.** Capacity, transactions, retrieval, retained versions, soft-delete window, redundancy and network access must be priced. |
| Maximum lifetime | 30 minutes of active use; any retained versions may outlive the session and must be costed before selection. |
| Baseline probes | Read three objects, record SHA-256/byte counts, create a separate backup/manifest, and verify destination absence. |
| Fault injection | Delete or corrupt exactly one lab object and prove the same read fails before recovery. |
| Diagnostics | Blob version/deletion metadata, pre-loss manifest, backup digest, access response and restore operation status. |
| Recovery | Restore to a new path; verify object count, exact hashes and the original read/application probe. |
| Teardown | Delete run-owned data/versions only where allowed by the approved retention policy; never claim immediate erasure if retention prevents it. |
| Residual-resource checks | Inspect objects, versions, snapshots, soft-deleted records, container, account and diagnostic settings. |
| Delayed billing checks | Reconcile stored versions/soft-deleted capacity, operations, retrieval, replication and egress after billing delay. |
| Classification | **Budget-deferred** |

## Selection and source notes

- LAB-L0-01 was completed read-only; see L0_READ_ONLY_PREFLIGHT.md. No App Service, VNet, NSG, NIC or route table appeared in the listable inventory, so IR-02 and IR-03 have no observed existing lab target. LAB-IR-11 is the only current new-resource candidate with an identified F1 region, Node 24 LTS runtime and published $0 compute tier. The 2026-11-27 inventory returned 0 visible F1/Free plans in Australia East; account entitlement and capacity remain NOT_VERIFIED. The earlier 0/2 interpretation is corrected. Capacity and name must be revalidated, and the batch still needs exact owner approval.
- The exact proposed candidate is LAB-IR-11 under the scope and constraints above. Potentially zero-cost does not mean approved or executed.
- The free Azure Resource Graph service is documented at [Microsoft Learn](https://learn.microsoft.com/en-us/azure/governance/resource-graph/overview). Candidate billing dependencies must be rechecked against the official [Private Link](https://azure.microsoft.com/en-us/pricing/details/private-link/), [DNS](https://azure.microsoft.com/en-us/pricing/details/dns/), [Virtual Network](https://azure.microsoft.com/en-us/pricing/details/virtual-network/), [Blob Storage](https://azure.microsoft.com/en-us/pricing/details/storage/blobs/), [Key Vault](https://azure.microsoft.com/en-us/pricing/details/key-vault/), [Azure Monitor](https://azure.microsoft.com/en-us/pricing/details/monitor/), [AKS](https://azure.microsoft.com/en-us/pricing/details/kubernetes-service/), [ACR](https://azure.microsoft.com/en-us/pricing/details/container-registry/), and [App Service Linux](https://azure.microsoft.com/en-us/pricing/details/app-service/linux/) pricing pages for the chosen region and offer.
- Expensive or structurally incompatible services remain outside the USD 1 shortlist: Azure Firewall, Virtual WAN, ExpressRoute, VPN Gateway, DNS Private Resolver endpoints, Application Gateway, Bastion, Front Door Premium, persistent AKS, paid ACR, persistent SQL, premium App Service, paid Defender plans, retained protected backup items, cross-region DR and full landing zones.
- Before any live mutation, add a lab-specific cost-ledger row with exact resource allowlist, current official pricing evidence, region/SKU, maximum runtime, dependencies, teardown/retention costs, gross cumulative estimate, USD 0.30 contingency and a separately approved batch scope. Stop if a reliable gross estimate cannot remain at or below USD 0.70.
