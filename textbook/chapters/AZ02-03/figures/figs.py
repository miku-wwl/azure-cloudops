"""Original diagrams for the Private DNS and Private Endpoint lecture."""

from figlib import Fig, NAVY, TEAL, ORANGE, RED, GREEN, MUTED


# Figure 5-1: an unchanged service hostname gets a context-dependent DNS answer.
f = Fig(760, 350)
f.text(380, 23, "同一个 Storage FQDN：linked zone 让私网客户端得到 PE IP", size=12, weight=700, color=NAVY, anchor="middle")
f.box(22, 98, 166, 82, "Application", ["settlementarchive.blob", ".core.windows.net"], "navy", title_size=10, size=8.6)
f.box(236, 98, 228, 82, "Public DNS CNAME", ["settlementarchive.blob...", "→ settlementarchive.privatelink..."] , "teal", title_size=10, size=8.4)
f.arrow((188, 139), (236, 139), color=NAVY, label="query original FQDN", dy=-8, label_size=7.6)
f.box(526, 55, 210, 84, "Linked private DNS zone", ["privatelink.blob.core.windows.net", "A → 10.60.4.7"], "green", title_size=9.5, size=7.8)
f.box(526, 197, 210, 84, "Public DNS continuation", ["no private answer visible", "→ Storage public endpoint IP"], "orange", title_size=9.5, size=8.0)
f.arrow((464, 121), (526, 97), color=GREEN, label="linked VNet / forwarded resolver", dx=2, dy=-7, label_size=7.5)
f.arrow((464, 157), (526, 236), color=ORANGE, label="unlinked / no forwarding", dx=-6, dy=2, label_size=7.8)
f.text(380, 314, "Application keeps the service FQDN; a linked zone with no A record returns NXDOMAIN unless Internet fallback is enabled.", size=8.7, color=MUTED, anchor="middle")
f.text(380, 334, "The privatelink name participates in DNS resolution; do not replace the Storage endpoint URL with that alias.", size=8.6, color=RED, anchor="middle")
f.save("dns-split-horizon.svg")


# Figure 5-2: a shared zone and resolver path extend DNS visibility to connected networks.
f = Fig(760, 358)
f.text(380, 23, "Hybrid 与 hub-spoke：让查询进入 linked VNet 的 DNS 解析路径", size=12, weight=700, color=NAVY, anchor="middle")
f.box(20, 94, 140, 78, "On-prem client", ["original Blob FQDN", "custom DNS"], "gray", title_size=9.2, size=8.1)
f.box(190, 78, 166, 108, "Conditional forwarder", ["blob.core.windows.net", "→ Azure resolver"], "orange", title_size=8.9, size=8.0)
f.box(388, 78, 164, 108, "Hub VNet", ["Private Resolver or", "DNS forwarder VM", "resolver VNet linked"], "navy", title_size=9.2, size=7.9)
f.arrow((160, 132), (190, 132), color=ORANGE, label="DNS", dy=-8, label_size=8)
f.arrow((356, 132), (388, 132), color=NAVY, label="forward", dy=-8, label_size=8)
f.box(588, 55, 150, 114, "Private DNS zone", ["privatelink.blob...", "VNet links → hub +", "client spokes", "A record managed"], "teal", title_size=9.1, size=7.7)
f.arrow((552, 110), (588, 110), color=TEAL, label="Azure DNS lookup", dy=-8, label_size=7.7)
f.box(567, 226, 171, 74, "Private Endpoint NIC", ["PE subnet · 10.60.4.7", "approved connection"], "green", title_size=9.1, size=8.0)
f.arrow((663, 169), (663, 226), color=GREEN, label="A → private IP", dx=42, dy=0, label_size=7.7)
f.box(22, 232, 520, 76, "Client VNets need DNS visibility", ["Link the same zone to each VNet that needs resolution; zone groups manage PE records.", "VNet links provide name resolution, not peering, routes, firewall passage, or data authorization."], "orange", title_size=9.1, size=7.9)
f.text(380, 340, "A DNS forwarder or Azure Private Resolver is a topology choice; do not assume one exists or is free.", size=8.6, color=MUTED, anchor="middle")
f.save("hybrid-dns-path.svg")


# Figure 5-3: resolution, network path, TLS identity, and data authorization are separate gates.
f = Fig(760, 376)
f.text(380, 23, "解析成功只是第一关：网络、TLS 主机名与数据授权各自决定结果", size=12, weight=700, color=NAVY, anchor="middle")
f.box(20, 108, 142, 74, "Original FQDN", ["settlementarchive.blob...", "DNS answer changes by client"], "navy", title_size=9.1, size=7.8)
f.box(196, 52, 166, 78, "Private answer", ["10.60.4.7", "PE connection Approved?"], "green", title_size=9.3, size=8.0)
f.box(196, 208, 166, 78, "Public answer", ["public endpoint IP", "public access enabled?"], "orange", title_size=9.3, size=8.0)
f.arrow((162, 133), (196, 92), color=GREEN, label="private A", dx=-4, dy=-8, label_size=7.8)
f.arrow((162, 157), (196, 247), color=ORANGE, label="public A", dx=-5, dy=8, label_size=7.8)
f.box(404, 108, 146, 74, "Network path", ["route + NSG + TCP", "not proved by DNS"], "teal", title_size=9.0, size=7.8)
f.arrow((362, 91), (404, 126), color=GREEN)
f.arrow((362, 247), (404, 162), color=ORANGE)
f.box(586, 51, 153, 80, "TLS hostname", ["client still uses the", "original service FQDN", "SNI / cert check"], "navy", title_size=9.0, size=7.7)
f.box(586, 154, 153, 80, "Data authorization", ["RBAC / SAS / key", "separate from DNS", "and PE approval"], "purple", title_size=8.8, size=7.7)
f.box(586, 256, 153, 58, "Request accepted", ["only if every gate passes"], "green", title_size=9.1, size=7.8)
f.arrow((550, 127), (586, 91), color=NAVY)
f.arrow((550, 153), (586, 191), color=TEAL)
f.arrow((662, 131), (662, 154), color=NAVY)
f.arrow((662, 234), (662, 256), color=GREEN)
f.text(380, 342, "Storage Private Endpoint traffic can work while public network access is disabled; DNS alone grants neither reachability nor data access.", size=8.4, color=RED, anchor="middle")
f.text(380, 362, "TLS/SNI implication is operational reasoning from the documented instruction to keep the original connection string; no TLS handshake is modeled.", size=7.9, color=MUTED, anchor="middle")
f.save("endpoint-access-gates.svg")
