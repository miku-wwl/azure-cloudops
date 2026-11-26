# AZ02-02 local NSG and ASG lab

This experiment evaluates a narrow fixture of custom IPv4 TCP/UDP NSG rules. It checks priority ordering, first-match behavior, source/destination ASG membership, subnet and NIC policy layers, and a simplified state table for the reverse side of an allowed connection. No Azure defaults, AVNM admin rules, service-tag expansion, ICMP, VM firewall, route, active probe, or platform API is emulated. An unmatched custom rule returns `NOT_MODELED_DEFAULT_RULES`.

From the repository root:

```powershell
Push-Location textbook/chapters/AZ02-02/labs/nsg-model
python -m unittest -v
python nsg_model.py
Pop-Location
```

Python 3.11 or later is required. No Azure CLI authentication, VM, Network Watcher, subscription or container is needed. All resources, addresses, groups and rules are fictional, and no cloud request or cost occurs.

For a future authorized live lab, use a running nonproduction VM and its actual NIC. Inspect both subnet and NIC associations, then use effective NSG / IP Flow Verify for one exact TCP/UDP tuple. Connection Troubleshoot sends active probes; check current availability, permissions, target authorization and cost before running it. No live operation is part of this offline experiment.
