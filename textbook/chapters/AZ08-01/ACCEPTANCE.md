# AZ08-01 acceptance — Azure hybrid routing and enterprise DNS

## V1.0.1 教材修订

- 补双向路由表、BGP 传播、原始 SQL 名称解析与 vWAN 关联、传播题解。
- 最终教材 [PDF](../../dist/pdf/AZ08-01_azure-hybrid-routing-enterprise-dns.pdf) 已用原出版工具重建。基线 7 页，修订 9 页。正文排入 5 个 SVG，保留 5 个可编辑图稿。最终页面已检查排版、图和代码，带入全套发布校验。
- 现有本地回归通过。新增云端步骤按文档例处理，历史证据与操作权限见 [V1.0.1 逐讲审查](../../V1_0_1_TEXTBOOK_REVIEW.md)。

- Acceptance date: 2026-11-27 (Pacific/Auckland)
- Gate: ACCEPTED for the offline lecture milestone only.
- Deliverable: `textbook/dist/pdf/AZ08-01_azure-hybrid-routing-enterprise-dns.pdf`
- PDF: 7 pages, 1,448,706 bytes; SHA-256 `3C54F564979B827DA8E436068FF1D827F51362ABFB8252D80884E730F7117161`.

## Scope and learning result

The chapter explains classic VNet peering and paired gateway-transit flags, the separate roles of BGP advertisement, route propagation and packet forwarding, ExpressRoute and S2S VPN coexistence, Azure Route Server, Standard Virtual WAN, and the inbound and outbound paths of Azure DNS Private Resolver. It teaches a direction-by-direction troubleshooting method for routing, DNS suffix selection, zone/ruleset association, return routes and UDP/TCP 53.

The evidence map is in [`textbook/SOURCE_MAP.md`](../../SOURCE_MAP.md). The chapter is grounded in Microsoft Learn and Azure Architecture Center sources covering [hub-spoke and peering](https://learn.microsoft.com/en-us/azure/networking/design-guide/hub-spoke), [VPN gateway transit](https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-peering-gateway-transit), [ExpressRoute/VPN coexistence](https://learn.microsoft.com/en-us/azure/expressroute/expressroute-howto-coexist-resource-manager), [Azure Route Server](https://learn.microsoft.com/en-us/azure/route-server/overview), [Virtual WAN](https://learn.microsoft.com/en-us/azure/virtual-wan/virtual-wan-about), and [Private Resolver](https://learn.microsoft.com/en-us/azure/dns/private-resolver-endpoints-rulesets). Sources were reviewed on 2026-11-27; volatile SKU, service-limit, regional-availability and price details are explicitly left for design-time recheck.

Five editable, original mechanism diagrams are included as SVGs with their Python source in `figures/figs.py`.

## Local verification

- The chapter build produced a 7-page PDF with 9,648 extracted characters and no placeholder markers. Render QA page fills were 20%, 98%, 96%, 72%, 95%, 91% and 53%; the publisher emitted its existing non-blocking Pillow `Image.getdata()` deprecation warning.
- All seven pages were rendered and visually reviewed as page pairs at 88 DPI and 140 DPI. Figures, type, table, references, page numbering and margins were legible, with no clipping or corruption.
- `hybrid_contract.py` passed its baseline of 13 checks. The chapter's offline unit suite passed 22 tests.
- The complete Python suite passed on Windows and in WSL: 375 tests across 21 lab directories, zero failing directories.
- Synthetic fixtures and tests exercise paired gateway-transit flags, BGP/propagation predicates, longest-prefix matching in both directions, resolver and ruleset links, longest DNS suffix, forwarding-loop risk, and UDP/TCP 53 path flags. The verifier is a narrow teaching contract. It is not an Azure Resource Manager parser, Azure emulator, BGP implementation, resolver or packet-path proof.

## Authorization, live scope and cost boundary

[`FUTURE-LIVE-READONLY.md`](labs/hybrid-connectivity/FUTURE-LIVE-READONLY.md) is a future procedure only. It is marked `NOT_RUN` and requires an L0 scope and a separately authorized, cost-reviewed run before use. No Azure authentication, subscription/account enumeration, management-plane request, DNS query, BGP/route operation, connectivity probe, resource change or billing query occurred for this acceptance. No Azure resource was created or changed.

The cost of any future live query set has not been estimated, and actual cumulative Azure spend remains `NOT_VERIFIED`; no actual USD 0.00 spend is claimed. The project-wide cumulative ceiling remains USD 1.00 and its planning threshold USD 0.70. This acceptance makes no live Azure or spend claim.

## Release decision

The PDF, editable figures, synthetic lab, documented runbook and source map meet the AZ08-01 offline lecture gate. They do not close Stage 1's final package check, Stage 2's lab/incident gates, or authorize Stage 3 live work.
