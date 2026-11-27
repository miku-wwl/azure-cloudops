# AZ08-01 hybrid connectivity contract lab

This exercise is local, synthetic, and offline. It checks a fictional bank's paired gateway-transit settings, two directions of route reachability, conditional DNS forwarding, longest-suffix rule selection, resolver reachability on UDP/TCP 53, and a documented Private Resolver loop hazard.

The checker does not parse Azure exports, connect to Azure, emulate BGP convergence, interpret Azure effective routes, run a DNS server, or prove packet delivery. Its input is an intentionally small teaching contract in `topology.json`; its longest-prefix selector demonstrates only address containment and prefix length. It does not reproduce all Azure route-source priorities, BGP best-path rules, Virtual WAN routing, NSGs, service endpoints, or application behavior.

## Run

From the repository root:

```powershell
python textbook/chapters/AZ08-01/labs/hybrid-connectivity/hybrid_contract.py
python -m unittest discover -s textbook/chapters/AZ08-01/labs/hybrid-connectivity/tests -p "test_*.py" -v
```

The fixture's clean-contract result is a local assertion about synthetic JSON, not an observed Azure topology. To practice diagnosis, copy `topology.json`, change one field at a time (for example `spoke_use_remote_gateway`, `bgp_session_up`, a route, `ruleset_linked_vnets`, or a DNS port flag), then pass the copy path to the script. Keep the expected control plane, route plane, and DNS plane separate in the diagnosis.
