# ADR-0002 — Hub-spoke and Virtual WAN

- Status: Accepted as a conditional reference choice; no network deployed.
- Date: 2026-11-27.
- Context: networking needs shared connectivity, east-west policy, hybrid integration and predictable operational ownership without assuming an enterprise hub is affordable for a lab.

## Decision

Use customer-managed hub-spoke as the enterprise reference starting point when regions/branches are limited and teams need direct control of the routing and shared services. Define explicit route tables, gateway transit, firewall/NVA paths and return-path checks; VNet peering alone is non-transitive. Evaluate Virtual WAN when branch count, global transit, cross-region connectivity or operations justify Microsoft-managed hub routing. Do not treat Virtual WAN as a cheaper synonym for hub-spoke.

For this repository's live-lab candidate, do not provision either hub model. Use one isolated scenario scope and no central network service; if the scenario cannot function without billable network infrastructure, mark it budget-deferred unless a separately reviewed estimate and authorization fit the project limits.

## Consequences

- Traditional hub-spoke keeps routing and appliance ownership explicit but increases customer routing and scaling work.
- Virtual WAN reduces some routing operations but adds hub, connection, gateway/scale-unit and traffic-processing charges.
- Both designs require route symmetry, firewall state, DNS and failure-domain review; neither guarantees application connectivity.
- The synthetic route lab cannot validate either live service.

## Source

- [Hub-and-spoke network topology](https://learn.microsoft.com/en-us/azure/networking/design-guide/hub-spoke)
- [Azure Virtual WAN topology and costs](https://learn.microsoft.com/en-us/azure/networking/design-guide/virtual-wan)
- [Spoke-to-spoke connectivity choices](https://learn.microsoft.com/en-us/azure/architecture/networking/spoke-to-spoke-networking)
