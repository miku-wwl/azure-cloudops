# AZ02-01 local route-selection lab

This lab is a small teaching model for IPv4 ordinary route selection. It loads synthetic subnet system/BGP routes and associated UDRs, applies longest-prefix matching, applies UDR > BGP > system on equal prefixes, and compares two explicitly modeled directions for one expected stateful appliance. It checks the next-hop enum and only accepts a next-hop IP for a `VirtualAppliance` route; known special next hops are automatically refused by the selector instead of relying on a fixture author to tag them manually. It refuses to guess when a documented special system-route rule or equal-best route falls outside the model.

From the repository root:

```powershell
Push-Location textbook/chapters/AZ02-01/labs/route-model
python -m unittest -v
python route_model.py
Pop-Location
```

Python 3.11 or later is required. The run makes no Azure request and creates no resource. No Azure CLI authentication, subscription, Network Watcher, VM, gateway, or appliance is needed. The JSON, VM addresses, route tables, NVA IPs and route decisions are fictional. Do not interpret a passing test or model output as proof of live effective routes, connectivity, route propagation, NVA session state, or Azure behavior.

The 16-test suite includes malformed next-hop spelling/IP checks and a service-endpoint route without a manual special-case tag. The accepted next-hop names and special-route boundary are tied to the Microsoft REST route schema and routing documentation; the model is still not a complete Azure route validator.

For an authorized future live lab, use a pre-existing nonproduction VM/NIC and an already available Network Watcher. Inspect current pricing and permissions before any diagnostic operation; collect the subnet association and NIC effective routes, query Next Hop for a specific source/destination, then independently validate the reverse path and application connection. No live operation is part of this offline experiment.
