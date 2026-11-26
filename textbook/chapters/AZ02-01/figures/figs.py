"""Original AZ02-01 route-selection and diagnostic diagrams."""

from figlib import Fig, NAVY, TEAL, ORANGE, RED, GREEN, MUTED


# Figure 3-1: longest prefix first, then source preference for equal prefixes.
f = Fig(760, 352)
f.text(380, 22, "先找匹配目的地址的最长前缀；只有同前缀才比较路由来源", size=12, weight=700, color=NAVY, anchor="middle")
f.group(24, 46, 712, 232, "payments subnet 的 effective routes（教学 fixture）", "plain", size=10.2)
f.box(42, 84, 190, 50, "172.20.40.0/24", ["UDR → NVA 10.20.0.4"], "green", title_size=10, size=8.8)
f.box(268, 84, 190, 50, "172.20.0.0/16", ["UDR → NVA .4", "BGP → VPN gateway"], "orange", title_size=10, size=8.4)
f.box(494, 84, 224, 50, "0.0.0.0/0", ["UDR → NVA .4", "system → Internet"], "teal", title_size=10, size=8.4)
f.arrow((232, 109), (268, 109), color=MUTED, dash=True)
f.arrow((458, 109), (494, 109), color=MUTED, dash=True)
f.text(136, 164, "目的 172.20.40.15", size=9.4, weight=700, color=GREEN, anchor="middle")
f.arrow((136, 150), (136, 134), color=GREEN)
f.text(362, 164, "目的 172.20.8.15", size=9.4, weight=700, color=ORANGE, anchor="middle")
f.arrow((362, 150), (362, 134), color=ORANGE)
f.box(44, 195, 320, 54, "第一步：最长匹配 /24", ["172.20.40.15 → 选 partner-segment"], "green", title_size=9.4, size=8.6)
f.box(396, 195, 322, 54, "第二步：同前缀来源优先级", ["172.20.8.15：/16 UDR 胜 BGP"], "orange", title_size=9.4, size=8.6)
f.text(380, 309, "VNet / peering / service endpoint system routes 有特殊规则；service endpoint route 不能由 UDR 覆盖。", size=8.8, color=RED, anchor="middle")
f.text(380, 335, "概念图不代表任一真实 NIC 的 effective route table。", size=8.8, color=MUTED, anchor="middle")
f.save("route-selection.svg")


# Figure 3-2: stateful inspection needs a valid return path through the intended instance.
f = Fig(760, 330)
f.text(380, 22, "单看去程路由不够：有状态检查还要确认回程经过同一检查实例", size=12, weight=700, color=NAVY, anchor="middle")
f.box(22, 82, 132, 60, "Payment VM", ["10.20.1.10"], "navy", title_size=9.8, size=8.5)
f.box(198, 82, 158, 60, "Forward UDR", ["172.20.40.0/24", "VirtualAppliance"], "teal", title_size=9.4, size=8.1)
f.box(404, 82, 145, 60, "NVA firewall A", ["10.20.0.4", "stateful session"], "green", title_size=9.2, size=8.2)
f.box(597, 82, 141, 60, "Partner", ["172.20.40.15"], "navy", title_size=9.8, size=8.5)
f.arrow((154, 112), (198, 112), color=NAVY, label="forward", dy=-7, label_size=8)
f.arrow((356, 112), (404, 112), color=GREEN)
f.arrow((549, 112), (597, 112), color=GREEN)
f.box(404, 205, 145, 60, "NVA firewall B", ["10.20.0.8", "different instance"], "red", title_size=9.2, size=8.2)
f.arrow((597, 142), (520, 205), color=ORANGE, label="return selection", label_at=0.45, dx=25, dy=-2, label_size=7.5)
f.arrow((404, 235), (154, 142), color=RED, label="return bypasses A", label_at=0.48, dx=-2, dy=5, label_size=7.7)
f.text(380, 294, "若 firewall A 不支持非对称转发或会话同步，回程到 B 可能被有状态检查丢弃。", size=9.0, color=RED, anchor="middle")
f.text(380, 317, "图中独立 route contexts 是逻辑示意；真实拓扑须逐跳核对。", size=8.7, color=MUTED, anchor="middle")
f.save("asymmetric-path.svg")


# Figure 3-3: selected-hop evidence and reachability evidence are separate.
f = Fig(760, 264)
f.text(380, 22, "用分层证据定位路由问题；Next Hop 只回答一个源到一个目的的选路", size=12, weight=700, color=NAVY, anchor="middle")
steps = [
    (24, "1 · Association", "VM NIC 属于哪个 subnet？\n该 subnet 关联哪张 route table？", "navy"),
    (210, "2 · Effective routes", "NIC 上有哪些 system、BGP、UDR？\n选中的 prefix / next hop 是什么？", "teal"),
    (396, "3 · Next Hop", "指定 source IP + destination IP\n返回 next-hop type / IP / route table", "orange"),
    (582, "4 · End-to-end", "分别检查去程与回程\n再验证 TCP、应用和业务结果", "green"),
]
for x, title, lines, style in steps:
    f.box(x, 82, 154, 102, title, lines.split("\n"), style, title_size=9.6, size=8.0)
for x in (178, 364, 550):
    f.arrow((x, 133), (x + 32, 133), color=MUTED)
f.text(380, 220, "某个方向的 Next Hop 正确，不证明回程、NSG、DNS、应用监听或数据授权正常。", size=9.1, color=RED, anchor="middle")
f.text(380, 247, "Effective routes 适用于 VM 网络接口；Network Watcher Next Hop 需要现有的 Network Watcher。", size=8.6, color=MUTED, anchor="middle")
f.save("diagnostic-sequence.svg")
