"""Original mechanism figures for AZ02-04."""

from figlib import Fig, NAVY, TEAL, ORANGE, RED, GREEN, MUTED


# Figure 6-1: the services operate at different scopes and protocol boundaries.
f = Fig(760, 337)
f.text(380, 23, "先确定流量边界，再选择入口服务", size=13, weight=700, color=NAVY, anchor="middle")
f.box(18, 55, 230, 218, "Azure Front Door", [
    "全球 edge；面向 HTTP / HTTPS", "跨 origin 做健康与路由", "TLS offload、缓存、规则", "WAF 能力按 Standard / Premium 核验", "更适合公网全球 Web/API 入口"
], "navy", title_size=12.2, size=9.7, lh=22, valign="top")
f.box(265, 55, 230, 218, "Application Gateway", [
    "regional 网络入口", "HTTP(S)：listener → rule → backend", "host/path routing、TLS termination", "WAF_v2 policy 可附着于资源/站点/路径", "同一资源也支持 TCP/TLS L4 proxy"
], "teal", title_size=11.5, size=9.2, lh=22, valign="top")
f.box(512, 55, 230, 218, "Azure Load Balancer", [
    "regional L4：TCP / UDP flows", "frontend + rule + backend pool", "默认按五元组 hash 分配 flow", "不检查 HTTP path/header，不卸载 TLS", "probe 决定新 flow 的 backend eligibility"
], "orange", title_size=11.7, size=9.2, lh=22, valign="top")
f.box(52, 291, 656, 35, "可能串联，但每一跳都有自己的健康判定、网络边界、失败证据与计费维度。", [], "gray", title_size=9.2)
f.save("traffic-boundaries.svg")


# Figure 6-2: request selection and backend-health evaluation are separate paths.
f = Fig(760, 374)
f.text(380, 23, "Application Gateway：请求规则引用后端；probe 与用户请求分开", size=12.5, weight=700, color=NAVY, anchor="middle")
f.box(20, 69, 125, 68, "Client", ["HTTPS request"], "navy", title_size=10.3, size=8.8)
f.box(182, 69, 136, 68, "Listener", ["IP / port / host"], "teal", title_size=10, size=8.7)
f.box(355, 69, 160, 68, "Routing rule", ["basic / path based"], "teal", title_size=10, size=8.6)
f.box(554, 69, 180, 68, "Backend pool", ["only healthy targets"], "green", title_size=10, size=8.6)
f.arrow((145, 103), (182, 103), color=NAVY, label="request", dy=-9, label_size=8.1)
f.arrow((318, 103), (355, 103), color=NAVY, label="match", dy=-9, label_size=8.1)
f.arrow((515, 103), (554, 103), color=GREEN, label="route", dy=-9, label_size=8.1)
f.box(220, 190, 202, 69, "Backend setting", ["protocol · port · host / SNI"], "orange", title_size=9.8, size=8.6)
f.box(477, 190, 247, 69, "Default or custom probe", ["path · host · status range · interval"], "orange", title_size=9.6, size=8.5)
f.arrow((435, 137), (326, 190), color=ORANGE, label="bind setting", dx=-5, dy=-6, label_size=8.2, curve=0)
f.arrow((422, 225), (477, 225), color=ORANGE, label="associated probe", dy=-8, label_size=8)
f.arrow((600, 190), (640, 137), color=ORANGE, label="probe each target", dx=9, dy=-8, label_size=8)
f.box(31, 287, 698, 59, "Separate paths", ["WAF policy inspects client requests; backend probes measure origin health.", "A client 403 and a probe 403 are different observations."], "gray", title_size=9.2, size=8.7, lh=12.5)
f.save("appgw-route-probe.svg")


# Figure 6-3: Front Door filters health before priority, latency and weights.
f = Fig(760, 372)
f.text(380, 23, "Front Door 先判断 origin 健康，再决定请求候选范围", size=12.5, weight=700, color=NAVY, anchor="middle")
steps = [
    (18, "可用 origin", ["enabled + probe healthy", "HTTP(S) 默认要求 200"], "navy"),
    (168, "Priority", ["保留数字最小的", "健康优先级组"], "teal"),
    (318, "Latency", ["保留 sensitivity", "范围内的 origin"], "teal"),
    (468, "Weight", ["在最终候选间", "按权重分配"], "orange"),
    (618, "请求候选集", ["session affinity", "可能固定后续请求"], "green"),
]
for x, title, lines, style in steps:
    f.box(x, 65, 128, 90, title, lines, style, title_size=9.6, size=8.1, lh=16, valign="top")
for left in (146, 296, 446, 596):
    f.arrow((left, 110), (left + 20, 110), color=NAVY, sw=1.3)
f.box(48, 203, 280, 96, "Primary unhealthy; backup healthy", ["probe removes priority 1", "priority 2 becomes eligible", "actual request path still needs evidence"], "green", title_size=9.4, size=8.3, lh=17, valign="top")
f.box(432, 203, 280, 96, "Every enabled origin unhealthy", ["documented fallback: round-robin", "across all origins", "do not assume fail-closed behavior"], "red", title_size=9.4, size=8.3, lh=17, valign="top")
f.text(380, 343, "Health-probe output and client request logs answer different questions; the local model reports only a candidate set.", size=8.8, color=MUTED, anchor="middle")
f.save("frontdoor-health-routing.svg")
