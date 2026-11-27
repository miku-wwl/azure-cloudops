# Future Azure observation runbook (read-only)

**Status: NOT_RUN.** This is a future plan for an owner-authorized, existing hybrid topology. It creates, updates, tests, disconnects, or deletes no Azure resource. Do not run it until the Stage 3 L0 scope, identity, exact subscription/resource allowlist, and query budget have been approved.

## Aim and prerequisites

Observe a single, already existing path from an approved workload spoke to an approved branch prefix, and its DNS lookups in both directions. Prefer a nonproduction fixture with an approved private FQDN. Do not use a live payment or customer name unless the data owner authorizes the query. Record an opaque case ID, UTC time, source subnet/NIC, destination prefix, DNS query name, and intended resolver path. Keep resource IDs, IPs, customer names, and command output in the approved local evidence store; redact before sharing.

Prerequisites are an owner-provided subscription/resource-group/VNet/NIC/gateway/resolver inventory; Azure CLI installed; the `dns-resolver` extension already present if its commands are needed; a corporate-side DNS client and an approved Azure-side test client already available; and explicit authorization to issue the exact management-plane reads and DNS questions listed below. Do not install an extension, change CLI context, sign in, enumerate subscriptions, or test DNS until the L0 instructions authorize those steps. The current Microsoft Learn CLI reference says `dns-resolver` commands require Azure CLI 2.75.0 or later and auto-install the extension on first use; check and approve that local change separately.

## Permission boundary

Use the already-assigned least-privilege identity. Do not grant a role during this lab. Relevant current provider operations include VNet and peering reads; gateway read plus `Microsoft.Network/virtualnetworkgateways/getbgppeerstatus/action` and `.../getlearnedroutes/action`; NIC read plus `Microsoft.Network/networkInterfaces/effectiveRouteTable/action`; DNS resolver and inbound/outbound endpoint reads; forwarding-ruleset, forwarding-rule, VNet-link and private-zone link reads. Check the current Microsoft permission reference for the exact case, resource type and casing. A generic `Reader` assignment may not contain these `action` operations. If an operation is denied, stop; do not broaden access to Network Contributor or add role assignments.

The permission strings above are source-analysed from [Azure permissions for Networking](https://learn.microsoft.com/en-us/azure/role-based-access-control/permissions/networking). CLI syntax is source-analysed from [VNet peering](https://learn.microsoft.com/en-us/cli/azure/network/vnet/peering?view=azure-cli-latest), [VNet Gateway](https://learn.microsoft.com/en-us/cli/azure/network/vnet-gateway?view=azure-cli-latest), [NIC effective routes](https://learn.microsoft.com/en-us/cli/azure/network/nic?view=azure-cli-latest), and the [DNS Resolver extension](https://learn.microsoft.com/en-us/cli/azure/dns-resolver?view=azure-cli-latest). Recheck the docs and effective role before execution.

## Read-only Azure CLI observations

Fill placeholders from the approved scope outside the repository. Run only those commands that are on the L0 allowlist. The first commands read paired peering settings; the next commands read BGP session/learned-prefix state and effective routes on an already-running NIC. These do not modify configuration.

```powershell
$subscription = '<approved-subscription-id>'
$hubResourceGroup = '<approved-hub-resource-group>'
$hubVnet = '<approved-hub-vnet>'
$spokeResourceGroup = '<approved-spoke-resource-group>'
$spokeVnet = '<approved-spoke-vnet>'
$gatewayName = '<approved-gateway-name>'
$nicName = '<approved-running-vm-nic>'

az network vnet peering list --resource-group $hubResourceGroup `
  --vnet-name $hubVnet --subscription $subscription `
  --query '[].{name:name,state:peeringState,remote:remoteVirtualNetwork.id,allowGatewayTransit:allowGatewayTransit,forwarded:allowForwardedTraffic}' -o json

az network vnet peering list --resource-group $spokeResourceGroup `
  --vnet-name $spokeVnet --subscription $subscription `
  --query '[].{name:name,state:peeringState,remote:remoteVirtualNetwork.id,useRemoteGateways:useRemoteGateways,forwarded:allowForwardedTraffic}' -o json

az network vnet-gateway list-bgp-peer-status --resource-group $hubResourceGroup `
  --name $gatewayName --subscription $subscription -o json

az network vnet-gateway list-learned-routes --resource-group $hubResourceGroup `
  --name $gatewayName --subscription $subscription -o json

az network nic show-effective-route-table --resource-group $spokeResourceGroup `
  --name $nicName --subscription $subscription -o json
```

When the extension is already approved and installed, inspect resolver endpoints and forwarding rules without running any `create`, `update`, `delete`, `link` mutation, or `test` command:

```powershell
$dnsResourceGroup = '<approved-resolver-resource-group>'
$resolverName = '<approved-resolver-name>'
$rulesetResourceGroup = '<approved-ruleset-resource-group>'
$rulesetName = '<approved-ruleset-name>'
$privateZoneResourceGroup = '<approved-private-zone-resource-group>'
$privateZoneName = '<approved-private-zone-name>'

az dns-resolver inbound-endpoint list --dns-resolver-name $resolverName `
  --resource-group $dnsResourceGroup --subscription $subscription -o json

az dns-resolver outbound-endpoint list --dns-resolver-name $resolverName `
  --resource-group $dnsResourceGroup --subscription $subscription -o json

az dns-resolver forwarding-ruleset list --resource-group $spokeResourceGroup `
  --virtual-network-name $spokeVnet --subscription $subscription -o json

az dns-resolver forwarding-rule list --resource-group $rulesetResourceGroup `
  --ruleset-name $rulesetName --subscription $subscription -o json

az dns-resolver vnet-link list --resource-group $rulesetResourceGroup `
  --ruleset-name $rulesetName --subscription $subscription -o json

az network private-dns link vnet list --resource-group $privateZoneResourceGroup `
  --zone-name $privateZoneName --subscription $subscription -o json
```

Only after the exact DNS queries and client hosts are approved, test one owner-approved name from each direction. Use existing clients and resolver infrastructure; this is a DNS request, not a management-plane `GET`.

```powershell
# On the approved corporate-side DNS test host:
Resolve-DnsName -Name '<approved-private-zone-fqdn>' -Server '<approved-inbound-endpoint-ip>' -Type A

# On the approved Azure workload host; use its configured Azure DNS path:
Resolve-DnsName -Name '<approved-corporate-fqdn>' -Type A
```

## Expected observations and decision rules

These are expectations, not results from this project. Both peering records should be `Connected`; gateway transit should have the hub-side allow and spoke-side use flags; BGP status should identify the expected peers; learned routes should include the expected remote prefixes; and the running NIC effective route output should contain a next hop for the approved destination. A BGP `Connected` state alone does not prove prefix acceptance or return reachability.

For the inbound DNS path, verify the corporate conditional-forwarder suffix and target, the endpoint's assigned private IP/subnet, network reachability and UDP/TCP 53 policy, and a private zone link to the inbound endpoint VNet. For Azure-to-corporate resolution, verify the source VNet's DNS mode, forwarding ruleset link, longest matching suffix, outbound endpoint association, destination DNS IP and port. A successful query is evidence for that name, client and time only; it does not prove the application transport path or every record.

If a control-plane read fails, distinguish authorization, missing resource and unsupported CLI/version before drawing a network conclusion. If BGP is up but the prefix is missing, inspect the peer's advertised/learned routes and propagation boundary. If forward routes exist but application traffic fails, record the independently evaluated return path and next hops. If IP routes pass but a DNS query fails, check resolver selection, zone/ruleset links, suffix and port 53 separately. Do not reset a gateway, edit peering, alter BGP policy, flush production caches, change DNS configuration, or repair Azure during this read-only run. A real repair requires its own reviewed and explicitly authorized scope.

## Recovery, cleanup and cost

The live procedure has no fault injection and no configuration recovery step. If a test unexpectedly changes a resource or sends an out-of-scope query, stop immediately, preserve the command/time/resource evidence and alert the owner through the approved channel. No cloud cleanup is expected because no resource is created. Delete only temporary, redacted local output when its retention requirement ends.

No Azure resource is deployed by these read-only commands. Management-plane calls are not resource runtime tests; DNS queries to an existing Private Resolver may be billable under the resolver's current pricing and may create operational logs. Before any DNS query, check official current regional pricing, query/endpoint billing terms, and the project ledger. Stop if reliable cumulative gross estimates cannot remain at or below USD 0.70. Actual Azure billing for this project remains `NOT_VERIFIED`; this runbook has not been executed.
