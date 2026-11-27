# Twelve incident contracts

Status at E7: all contracts were specified; none of the twelve had been executed as a live Azure incident. E8 later verified all eight mandatory local scenarios; the four non-mandatory incidents remain design-only. No local result is represented as a live Azure pass.

## Status and scope vocabulary

- `CONTRACTED_NOT_RUN`: the failure and recovery contract exists; this document is not an execution record.
- `LOCAL_VERIFIED`: the named local execution has actual failure, root-cause, same-probe recovery, and cleanup evidence; it does not verify Azure behavior.
- `MANDATORY_LOCAL_E8`: actual local failure, diagnosis, recovery and cleanup are required at E8.
- `DESIGN_ONLY`: no local pass is required; the Azure control-plane behavior remains unverified.
- Local experiments use a unique tool-owned temporary directory, namespace or context. They must not touch employer, customer, shared, production, default-host firewall, default DNS, or non-lab Terraform state.
- Azure resource scope, actual permissions, prices, SKU, region and subscription remain unknown until the authorized Stage 3 L0 review. Stage 2 performs no Azure resource creation or modification.

## IR-01 — Private DNS resolution failure

- **Lecture mapping:** AZ02-03; integrated diagnosis in AZ06-02.
- **Execution class / verification status:** `MANDATORY_LOCAL_E8`; `LOCAL_VERIFIED` at E8 (see [`IR-01_local-dns.json`](evidence/IR-01_local-dns.json)). Live Azure status: `NOT_RUN`.
- **Healthy baseline:** An explicitly addressed local DNS fixture returns the expected A record for the lab FQDN and the same application probe returns the expected HTTP status/content.
- **Target scope:** One run-owned UDP DNS listener, synthetic zone and local health endpoint. Future Azure scope is one owner-approved lab RG, private DNS zone/link and endpoint; no shared zone or production resolver.
- **Fault mechanism:** Remove the exact fixture A record or return NXDOMAIN for only the lab FQDN. Do not edit machine-wide resolver settings or public DNS.
- **Expected failure category:** DNS name-not-found or incorrect-address; distinguish it from TCP refusal/timeout and application failure.
- **Diagnostic hypotheses:** Wrong FQDN/suffix; missing or stale record; client using the wrong resolver; network path failure after successful resolution.
- **Discriminating probes:** Query the explicit resolver for the exact FQDN; compare the returned record with the fixture; attempt TCP only if an address is returned; call the baseline HTTP probe.
- **Root-cause evidence:** Captured DNS question/response and zone fixture show the exact missing or incorrect record; same request fails before application connection.
- **Minimal repair:** Restore only the intended A record in the run-owned zone; do not add public fallback or broaden suffix search.
- **Same-probe recovery:** Repeat the exact DNS query and identical URL probe; assert the intended address and expected HTTP result.
- **Negative assertions:** Unrelated FQDN remains unchanged; no TCP request follows NXDOMAIN; no public resolver, host DNS setting or unapproved address is used.
- **Cleanup:** Stop the fixture and health server; delete only the run-owned temporary directory; verify the listener ports are closed.
- **Required permissions:** Local user-level loopback sockets only. Azure observation would require narrowly scoped DNS/PE reads; changing a live record requires explicit owner approval and write permission limited to the lab zone.
- **Cost assumptions:** Local Azure cost is none. Live DNS, endpoint and any traffic cost are `NOT_ESTABLISHED`; price and dependencies must be checked at L0.

## IR-02 — Network filtering / NSG failure

- **Lecture mapping:** AZ02-02 and AZ02-04; integrated diagnosis in AZ06-02.
- **Execution class / verification status:** `MANDATORY_LOCAL_E8`; `LOCAL_VERIFIED` at E8 (see [`IR-02_local-filter.json`](evidence/IR-02_local-filter.json)). Live Azure status: `NOT_RUN`.
- **Healthy baseline:** In a dedicated network namespace, the selected client reaches one test listener on an allowed tuple while a negative-control port remains unreachable.
- **Target scope:** One disposable Linux network namespace, veth pair, loopback listener and namespace-local firewall rule set. Never alter the host firewall or default network namespace. Future Azure scope is a single lab NIC/subnet and NSG.
- **Fault mechanism:** Add one drop rule for the exact test source, destination, protocol and port; preserve DNS and the unrelated allowed tuple.
- **Expected failure category:** TCP connect timeout/reset with DNS and route baseline intact; for Azure, effective NSG rule denial is a separate evidence item.
- **Diagnostic hypotheses:** DNS error; missing route; firewall drop; listener not bound; wrong destination port.
- **Discriminating probes:** Resolve the local target; inspect namespace route; capture firewall rule/counter; run the same TCP probe to allowed and denied ports; inspect listener bind state.
- **Root-cause evidence:** Exact tuple counter increments on the isolated drop rule while the control tuple succeeds and the route/listener remain healthy.
- **Minimal repair:** Remove the one run-owned drop rule; do not add a broad allow rule.
- **Same-probe recovery:** Repeat the denied TCP probe and confirm success; repeat the negative-control denied port and confirm it remains blocked.
- **Negative assertions:** No command targets the host firewall or default network namespace; container networking is `none`; no external destination is contacted.
- **Cleanup:** Remove namespace, veth pair and owned rules; verify no namespace/device/rule remains and host connectivity is unchanged.
- **Required permissions:** `CAP_NET_ADMIN` for the disposable namespace only; the implementation must fail before changes if namespace isolation is unavailable. Azure checks need scoped NIC effective-NSG reads; a live rule change requires separately approved NSG write permission.
- **Cost assumptions:** Local Azure cost is none. Any live VNet, traffic or Network Watcher cost is `NOT_ESTABLISHED`; verify exact rates and dependencies at L0.

## IR-03 — Incorrect UDR / next-hop routing

- **Lecture mapping:** AZ02-01; integrated diagnosis in AZ06-02.
- **Execution class / verification status:** `DESIGN_ONLY`; `CONTRACTED_NOT_RUN`. Live Azure status: `NOT_RUN`.
- **Healthy baseline:** An approved lab route table has the intended longest-prefix route and supported next hop; the target responds through the expected path.
- **Target scope:** One exact route-table entry and one non-production destination prefix in an owner-approved isolated lab VNet. No default route, shared hub, gateway or NVA change.
- **Fault mechanism:** In a specifically approved lab only, change one test prefix to a wrong supported next-hop target or remove the intended route; Stage 2 never performs this mutation.
- **Expected failure category:** Route/next-hop mismatch or blackhole; distinct from NSG denial and DNS failure.
- **Diagnostic hypotheses:** More-specific route wins; wrong next-hop type/address; route absent/disabled; effective route differs from configured UDR; NSG blocks after routing.
- **Discriminating probes:** Compare route-table source with effective NIC routes; evaluate longest prefix and next-hop; check NSG separately; run the same target probe only within the approved lab.
- **Root-cause evidence:** Effective route for the exact target prefix points to the unexpected next hop or no route, with scope and timestamp recorded.
- **Minimal repair:** Restore the one approved prefix/next-hop entry; do not replace default routing or broaden prefixes.
- **Same-probe recovery:** Re-read effective routes and repeat the same destination probe; retain the route and probe evidence.
- **Negative assertions:** No peering, gateway, firewall, DNS, or unrelated route is changed; no traffic is sent to a non-lab prefix.
- **Cleanup:** Restore original route-table state, verify effective routes, and inspect for residual route entries.
- **Required permissions:** Local design needs no elevated permission. Azure reads require exact NIC/route-table network read; mutation requires explicit owner approval and route-table write at the lab scope.
- **Cost assumptions:** Live route-table configuration has no standalone estimate here, but VNet/NVA/gateway and traffic dependencies may cost. Gross cost is `NOT_ESTABLISHED` pending L0.

## IR-04 — VNet peering connectivity failure

- **Lecture mapping:** AZ08-01; integrated diagnosis in AZ06-02.
- **Execution class / verification status:** `DESIGN_ONLY`; `CONTRACTED_NOT_RUN`. Live Azure status: `NOT_RUN`.
- **Healthy baseline:** Two specifically approved lab VNets have reciprocal peering state, address spaces do not overlap, intended forwarding/gateway flags are paired, and a scoped test path works.
- **Target scope:** A dedicated two-VNet lab only. A local bridge, veth or container network is not Azure VNet peering and cannot verify Azure peering semantics.
- **Fault mechanism:** For an authorized live exercise only, disable/remove one side of the lab peering or alter one required forwarding flag; no Stage 2 change is allowed.
- **Expected failure category:** Peering disconnected/asymmetric configuration, missing forwarded-traffic permission, or route propagation issue.
- **Diagnostic hypotheses:** One-sided peering; overlapping address space; forwarded traffic disabled; gateway transit mismatch; effective route or NSG denial.
- **Discriminating probes:** Read both peering objects and state; compare address spaces and paired flags; inspect effective routes/NSGs on both sides; use one approved path probe.
- **Root-cause evidence:** The reciprocal peering or required flag differs on a named side and aligns with missing effective route/connectivity.
- **Minimal repair:** Restore only the mismatched lab peering state or paired setting; do not add a broad route or gateway.
- **Same-probe recovery:** Confirm both sides report connected, expected routes exist, and the same scoped path probe succeeds.
- **Negative assertions:** No hub/spoke, gateway, Route Server, NVA or production peering is altered; no unapproved transitive path is claimed.
- **Cleanup:** Restore pre-run state or delete only owner-approved lab peerings/VNets; enumerate residual peering and network resources.
- **Required permissions:** Exact-scope VNet/peering/route reads; live mutation requires explicit owner approval and both-side network write authorization.
- **Cost assumptions:** Peering data transfer and supporting resources may be billable. Cost is `NOT_ESTABLISHED`; classify as budget-deferred until current pricing/account eligibility is confirmed.

## IR-05 — Managed Identity / RBAC permission denied

- **Lecture mapping:** AZ03-01, AZ03-02 and AZ04-04; integrated diagnosis in AZ06-02.
- **Execution class / verification status:** `MANDATORY_LOCAL_E8`; `LOCAL_VERIFIED` at E8 (see [`IR-05_local-permissions.json`](evidence/IR-05_local-permissions.json)). Live Azure status: `NOT_RUN`.
- **Healthy baseline:** A run-owned unprivileged OS principal can read one explicitly granted fixture object, cannot write it, and cannot read a neighboring out-of-scope object.
- **Target scope:** One temporary directory and a dedicated test principal/group in the local Linux permission database/credentials; no user-home or repository permissions change. Future Azure scope is one data object/container and one workload identity.
- **Fault mechanism:** Remove only the fixture principal's read bit and invoke the same read operation as that principal; retain evidence of the OS `EACCES` result.
- **Expected failure category:** Authorization denied after successful process identity selection; distinguish from process/authentication startup failure and missing file.
- **Diagnostic hypotheses:** Wrong principal; missing exact read grant; incorrect object path; parent-directory traversal denial; unrelated authentication failure.
- **Discriminating probes:** Record effective UID/GID; inspect only fixture ownership/mode; attempt the read as the principal; compare existence as lab owner; confirm write/out-of-scope controls are denied.
- **Root-cause evidence:** Same principal and object exist, but the exact required read permission is absent and the kernel returns permission denied.
- **Minimal repair:** Grant only group read on the one fixture file; no directory write, sudo, root execution or broad role.
- **Same-probe recovery:** Repeat the exact read as the same principal and verify the expected digest; re-run write and neighboring-object negative controls.
- **Negative assertions:** Principal cannot write, enumerate unrelated paths, or read the negative-control object; no Azure role is granted and no token is acquired.
- **Cleanup:** Stop child processes, remove the run-owned directory, temporary group/identity artifacts if created, and verify original system account/group state is unchanged.
- **Required permissions:** Local setup may require root inside the disposable WSL environment to set file ownership and drop child privileges; never edit host accounts. Azure reads require exact identity/role-assignment and data-plane evidence; a live role change requires explicit approval and minimal data role.
- **Cost assumptions:** Local Azure cost is none. Live managed-identity, Storage/Key Vault and monitoring dependencies are `NOT_ESTABLISHED`; estimate at L0.

## IR-06 — Key Vault access failure

- **Lecture mapping:** AZ03-02 and AZ04-04; integrated diagnosis in AZ06-02.
- **Execution class / verification status:** `DESIGN_ONLY`; `CONTRACTED_NOT_RUN`. Live Azure status: `NOT_RUN`.
- **Healthy baseline:** In a specifically authorized lab vault, the workload can retrieve only the approved test secret metadata/value required by its contract; secret values are never written to evidence.
- **Target scope:** One owner-approved vault and one synthetic secret/version. No shared vault, production secret, broad subscription role or real credential.
- **Fault mechanism:** Select one controlled condition: deny the exact data-plane permission, use the wrong token audience, or block the approved network path. Never combine causes in one run.
- **Expected failure category:** Network/TLS, token audience/authentication, data-plane RBAC, or secret state/not-found; not a generic “Key Vault failed” label.
- **Diagnostic hypotheses:** DNS/private endpoint; firewall/network ACL; TLS/name mismatch; token audience/principal; missing data role/scope; disabled/expired/incorrect secret version.
- **Discriminating probes:** Check DNS/TCP/TLS; inspect only vault public-network/RBAC metadata; inspect token claims only from an approved existing token; read role assignments and secret attributes without printing secret content.
- **Root-cause evidence:** One category-specific observation matches the selected injected condition; other layers are shown healthy or explicitly unverified.
- **Minimal repair:** Restore the one altered network setting, exact data role or intended secret state; never grant Owner or list/read unrelated secrets.
- **Same-probe recovery:** Repeat the approved application operation and verify only status/digest/expected non-secret result.
- **Negative assertions:** No secret value, unrelated secret name, access token or credential is logged; no role is broadened beyond the one object/use case.
- **Cleanup:** Remove the synthetic secret and owned vault resources only under separately approved cleanup authorization; enumerate residual resources and delayed cost.
- **Required permissions:** Read-only vault, network, role and secret-attribute reads at exact scope; data-plane test needs the single approved operation; any configuration/role/secret mutation needs owner approval.
- **Cost assumptions:** Vault tier, operations, private endpoint and DNS dependencies may be billable. Cost is `NOT_ESTABLISHED`; do not include in a USD 1 run without current estimate and explicit batch approval.

## IR-07 — AKS / ACR image-pull failure

- **Lecture mapping:** AZ04-03 and AZ03-02; integrated diagnosis in AZ06-02.
- **Execution class / verification status:** `MANDATORY_LOCAL_E8`; `LOCAL_VERIFIED` at E8 (see [`IR-07_local-kind.json`](evidence/IR-07_local-kind.json)). Live Azure status: `NOT_RUN`.
- **Healthy baseline:** In an isolated local Kubernetes cluster and namespace, a known preloaded local image starts, the Pod becomes Ready, and its functional HTTP probe passes.
- **Target scope:** One disposable local cluster, one namespace, one synthetic image and one run-owned registry or preloaded image. No default/shared cluster. If a usable container engine is unavailable, mark blocked; never fabricate Pod events or silently replace this requirement with a Python fixture.
- **Fault mechanism:** Deploy a unique nonexistent tag against a loopback-only local Distribution API fixture and capture the actual kubelet-generated `ErrImagePull`/`ImagePullBackOff` Pod condition and event. The local API returns HTTP 404 `MANIFEST_UNKNOWN`; no public registry or ACR is contacted.
- **Expected failure category:** Image reference/not-found. Authentication, registry reachability, TLS and rate-limit failures are separate hypotheses and are not implied by a missing tag.
- **Diagnostic hypotheses:** Wrong repository/tag/digest; registry auth; DNS/route/TLS; node egress; architecture mismatch; rate limiting.
- **Discriminating probes:** `kubectl describe pod`; fetch timestamped namespace warning events; verify exact image reference and node status; test registry name/path only from the cluster; do not read or print Secret objects.
- **Root-cause evidence:** Real Pod status/event names the missing reference or registry response and matches the exact manifest image field.
- **Minimal repair:** Change only the image to the existing known digest/tag; do not attach broader registry credentials or alter cluster-wide pull policy.
- **Same-probe recovery:** New Pod pulls the corrected image, reaches Ready, and passes the same application probe; negative invalid tag remains rejected in a separate disposable Pod if safely retained for evidence.
- **Negative assertions:** No credentials are emitted; no cluster-wide secret/RBAC changes; no Azure ACR/AKS success is inferred from local registry behavior.
- **Cleanup:** Delete only the namespace/workloads/registry created by this run; verify Pods, events, images and cluster resources are absent; remove the cluster only if it is run-owned.
- **Required permissions:** Local cluster-admin for the disposable cluster/namespace and local container-engine access. Live Azure diagnosis needs scoped AKS read and ACR pull evidence; any identity/role/network repair requires separate approval.
- **Cost assumptions:** Local engine/cluster cost is none in Azure. AKS/ACR, nodes, disk, networking and egress are not assumed free; live gross cost is `NOT_ESTABLISHED` and budget-deferred pending L0.

## IR-08 — Terraform State locking and drift

- **Lecture mapping:** AZ07-02 and AZ07-01; pipeline context in AZ07-03; integrated diagnosis in AZ06-02.
- **Execution class / verification status:** `MANDATORY_LOCAL_E8`; `LOCAL_VERIFIED` at E8 using a state-changing competing `terraform apply` and real local file drift (see [`IR-08_local-terraform.txt`](evidence/IR-08_local-terraform.txt)). E4 remains separate historical evidence. Live Azure status: `NOT_RUN`.
- **Healthy baseline:** A fresh tool-owned copy initializes a local backend, applies only `terraform_data`/local-file resources, records state serial and content digest, and a no-change plan reports no diff.
- **Target scope:** One unique temporary checkout/state directory with no Azure providers or remote backend. Future scope is one owner-approved remote state key and one planned target RG only after L0/explicit batch approval.
- **Fault mechanism:** A first Terraform process holds the real backend lock while a second process attempts a state-changing operation; separately mutate one managed local file outside Terraform to create actual drift.
- **Expected failure category:** Backend lock contention from the second operation and resource drift from an observed content mismatch; do not substitute elapsed sleep or a handwritten lock message.
- **Diagnostic hypotheses:** Live lock holder; stale lock; wrong backend/workspace; external file writer; provider refresh/configuration mismatch.
- **Discriminating probes:** Capture Terraform's actual lock refusal and lock ID; verify first process owns the lock; inspect state lineage/serial; run plan after out-of-band edit and inspect actual diff; compare file digest.
- **Root-cause evidence:** Real second process refuses while first holds lock; actual plan identifies changed managed file; State and config are limited to the unique copy.
- **Minimal repair:** Wait for the actual holder to release; never force-unlock an active lock. Reconcile the local file through a reviewed Terraform apply and verify updated state/content.
- **Same-probe recovery:** Retry the operation after owner exits; run a final plan and file digest check, both showing the intended state.
- **Negative assertions:** No remote Azure backend, `azurerm` provider, credential environment or cloud operation; no force-unlock; unrelated State is untouched.
- **Cleanup:** Terraform destroy in the disposable copy, remove it, check for Terraform processes and residual files, and preserve only sanitized evidence.
- **Required permissions:** Local user access to the temporary directory and Terraform binary. Azure remote State would require exact blob data-plane permissions; no credential is supplied in E8.
- **Cost assumptions:** Local Azure cost is none. Remote state account/transactions are existing-resource dependent and `NOT_ESTABLISHED`; any remote init is deferred to explicit Stage 3 authorization.

## IR-09 — Azure Policy deployment denial

- **Lecture mapping:** AZ03-03 and AZ07-01; integrated diagnosis in AZ06-02.
- **Execution class / verification status:** `DESIGN_ONLY`; `CONTRACTED_NOT_RUN`. Live Azure status: `NOT_RUN`.
- **Healthy baseline:** For a future approved lab RG, record assigned Policy definition/effect/exclusions and one known-compliant planned resource; no deployment occurs in this contract.
- **Target scope:** One owner-approved resource and policy assignment scope. No management-group or subscription-wide policy edit; no policy exemption without owner decision.
- **Fault mechanism:** An explicitly authorized live test may attempt one narrowly invalid resource property under a pre-existing `Deny` assignment; Stage 2 and this spec do not submit the request.
- **Expected failure category:** ARM Policy `RequestDisallowedByPolicy`/deny, distinguished from provider validation, RBAC, quota and service errors.
- **Diagnostic hypotheses:** Deny assignment; wrong policy scope/effect; exemption or excluded scope; invalid provider property; caller permission/quota.
- **Discriminating probes:** Read policy assignment/definition and compliance state; inspect exact error code, policy assignment/definition IDs and evaluated resource fields; compare with a compliant plan without applying.
- **Root-cause evidence:** Denial payload identifies the exact policy/assignment and offending field at the target scope.
- **Minimal repair:** Correct the noncompliant resource property in IaC; do not disable the policy or request an exemption as a troubleshooting shortcut.
- **Same-probe recovery:** Recreate a plan showing the compliant value and, only after separate deployment approval, verify the same operation no longer receives the Policy denial.
- **Negative assertions:** No policy assignment/definition is modified; no subscription-wide exception; no successful creation is claimed from a local fixture.
- **Cleanup:** If a separately approved live run created anything, delete only its allowlisted resources, verify policy state and residuals, and reconcile delayed charges.
- **Required permissions:** Read policy states/assignments/definitions at exact scope; live deployment needs resource-specific write authorization; Policy changes require separate governance-owner approval.
- **Cost assumptions:** Policy queries/design are not a resource price estimate. Any supporting live resource costs are `NOT_ESTABLISHED`; price at L0.

## IR-10 — Monitoring and alert failure

- **Lecture mapping:** AZ05-01 and AZ05-02; integrated diagnosis in AZ06-02.
- **Execution class / verification status:** `MANDATORY_LOCAL_E8`; `LOCAL_VERIFIED` at E8 (see [`IR-10_local-alert.json`](evidence/IR-10_local-alert.json)). Live Azure status: `NOT_RUN`.
- **Healthy baseline:** A local health service returns expected status; direct probe observations are timestamped and ingested into a local telemetry file/collector; a configured rule remains resolved for healthy measurements.
- **Target scope:** One run-owned local HTTP service, probe client, telemetry store and alert evaluator. Every measurement must come from a real request/response; do not create synthetic alert events or fabricate log rows.
- **Fault mechanism:** Introduce a service response failure and independently configure one known bad alert threshold; verify telemetry contains the measured failure but the broken rule does not activate, then repair the threshold.
- **Expected failure category:** Telemetry/alert evaluation gap (signal absent, late, mis-scoped, wrong threshold or state transition) distinct from service failure.
- **Diagnostic hypotheses:** Probe not running; telemetry not written; wrong time window; wrong service/resource scope; incorrect predicate; stale alert state.
- **Discriminating probes:** Send the same real HTTP probes; inspect raw timestamp/status observations; recompute rule result from those rows; inspect alert transition and recovery state.
- **Root-cause evidence:** Measured failing responses are present in the local telemetry, while the incorrect predicate evaluates false; corrected predicate evaluates from the same measurements and raises the expected state.
- **Minimal repair:** Correct only the target/window/threshold; do not alter the service fault or invent a notification.
- **Same-probe recovery:** Re-run the identical HTTP request after restoring the service; verify new successful telemetry and a resolved alert state.
- **Negative assertions:** No alert transition is written by hand; no sleep-only evidence; no Azure Monitor/action group/notification is claimed; missing data is not treated as healthy.
- **Cleanup:** Stop local servers/evaluator, remove owned telemetry and temporary data, verify no listener/process remains.
- **Required permissions:** Local user-level processes only. Azure reads need exact metric/alert/workspace scope; live signal or alert changes and action-group delivery require explicit owner approval.
- **Cost assumptions:** Local Azure cost is none. Azure Monitor ingestion, retention, metric alerts and action delivery may incur charges; live cost is `NOT_ESTABLISHED` pending L0.

## IR-11 — Deployment regression and rollback

- **Lecture mapping:** AZ04-02 and AZ07-03; integrated diagnosis in AZ06-02.
- **Execution class / verification status:** `MANDATORY_LOCAL_E8`; `LOCAL_VERIFIED` at E8 (see [`IR-11_local-rollback.json`](evidence/IR-11_local-rollback.json)). Live Azure status: `NOT_RUN`.
- **Healthy baseline:** A local versioned application release returns its expected API result, build/version identifier and health status through one stable URL.
- **Target scope:** One run-owned local service and two immutable release directories/artifacts. No production app, cloud resource, cluster or shared deployment target.
- **Fault mechanism:** Atomically point the local deployment to a deliberately regressed release that starts but returns a functional error/content mismatch; capture the actual request and version.
- **Expected failure category:** Deployment regression at application behavior; distinguish healthy process/container from healthy function.
- **Diagnostic hypotheses:** Bad artifact; wrong active release pointer; configuration mismatch; stale client; dependency/data incompatibility.
- **Discriminating probes:** Call the same functional URL before/after deployment; record status, response assertion and release ID; inspect the active pointer and artifact checksum.
- **Root-cause evidence:** The regressed artifact is active and its real response violates the baseline contract; the old artifact passes the identical request.
- **Minimal repair:** Atomically restore the prior known-good release pointer; do not change data, secrets or routing to mask the defect.
- **Same-probe recovery:** Call the same URL and assert expected status/content/version and any required state invariant; confirm the prior artifact checksum.
- **Negative assertions:** A running process alone is not accepted; no user data is lost; no Terraform apply or unapproved cloud deployment is used.
- **Cleanup:** Stop server, remove run-owned releases and pointer, verify port and child process are gone.
- **Required permissions:** Local user can launch and stop the run-owned process and write its temporary release directory. Azure deployment requires a separately approved narrowly scoped pipeline/environment and rollback permission.
- **Cost assumptions:** Local Azure cost is none. Any App Service/container deployment cost is `NOT_ESTABLISHED`; do not deploy pending L0 and explicit batch authorization.

## IR-12 — Data loss and restoration

- **Lecture mapping:** AZ06-01, AZ04-04 and AZ06-02.
- **Execution class / verification status:** `MANDATORY_LOCAL_E8`; `LOCAL_VERIFIED` at E8 (see [`IR-12_local-restore.json`](evidence/IR-12_local-restore.json)). Live Azure status: `NOT_RUN`.
- **Healthy baseline:** A run-owned synthetic dataset has a recorded ordered object list, byte counts, SHA-256 manifest and successful read probe.
- **Target scope:** One temporary source directory and one immutable backup copy; restoration must target a separate new path. No real business, customer or employer data.
- **Fault mechanism:** Create and verify the backup, then delete or corrupt one source-only object and demonstrate the source checksum/read fails.
- **Expected failure category:** Data-integrity loss in the source; distinguish it from a missing manifest, unreadable backup or application path issue.
- **Diagnostic hypotheses:** Wrong backup generation; incomplete object set; checksum mismatch; restore path collision; permission/serialization issue.
- **Discriminating probes:** Recompute source/backup hashes and object counts; read affected record from source and backup independently; verify restore destination was initially absent.
- **Root-cause evidence:** Source object is absent/corrupt while the matching backup bytes and manifest remain intact.
- **Minimal repair:** Restore the selected backup object into the new isolated path; do not overwrite the source or unrelated files.
- **Same-probe recovery:** Verify exact object count, per-object hashes, read behavior and end-to-end application fixture; record elapsed recovery time.
- **Negative assertions:** Source loss is observable before restore; backup remains immutable; checksum is not recomputed from the corrupted source; no success is inferred from directory existence alone.
- **Cleanup:** Remove only source/backup/restore paths owned by the run after evidence is recorded; verify no residual data remains.
- **Required permissions:** Local user-level read/write within the run-owned temp directory. Azure Backup/Storage/SQL validation requires separately approved exact resource and data-plane scope.
- **Cost assumptions:** Local Azure cost is none. Azure Backup, snapshots, Storage, SQL restore and retained recovery points may be billable; costs are `NOT_ESTABLISHED` and require L0 pricing/cleanup review.
