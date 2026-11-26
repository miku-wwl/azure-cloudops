"""Original AZ01-01 reliability figures; generated with textbook/tools/figlib.py."""

from figlib import Fig, NAVY, TEAL, ORANGE, RED, GREEN, MUTED


# Figure 2-1: distinct blast-radius boundaries; none implies the next.
f = Fig(760, 330)
f.text(380, 22, "故障域从局部到广域：每层需要不同的设计与恢复动作", size=12, weight=700, color=NAVY, anchor="middle")
f.group(26, 46, 218, 224, "Host / Rack", "plain", size=10.5)
f.box(43, 86, 184, 54, "VM Availability Set", ["FD：分开共享电源 / 交换机", "UD：计划维护分批重启"], "teal", title_size=10.4, size=8.7)
f.box(43, 166, 184, 70, "不覆盖", ["应用与 OS 缺陷", "共享 datacenter 故障", "Zone / Region outage"], "gray", title_size=10.2, size=8.8)
f.group(270, 46, 218, 224, "Availability Zone", "region", size=10.5)
f.box(287, 86, 184, 54, "单 Zone / zonal", ["固定一处物理隔离域", "故障时需工作负载切换"], "orange", title_size=10.4, size=8.7)
f.box(287, 166, 184, 70, "Zone-redundant", ["服务按产品机制跨区", "仍要检查依赖与容量", "责任随 IaaS / PaaS 变化"], "green", title_size=10.2, size=8.8)
f.group(514, 46, 218, 224, "Azure Region", "danger", size=10.5)
f.box(531, 86, 184, 54, "Region outage", ["单 Region 多区仍失效", "启动跨区 recovery path"], "red", title_size=10.4, size=8.7)
f.box(531, 166, 184, 70, "Recovery decision", ["RTO / RPO 与驻留限制", "复制 / 备份 / 重建", "验证服务与数据完整"], "white", title_size=10.2, size=8.8)
f.arrow((244, 157), (270, 157), color=ORANGE)
f.arrow((488, 157), (514, 157), color=RED)
f.text(380, 307, "图中为概念范围；SKU、Region 支持与故障责任必须按具体服务文档确认。", size=9.3, color=MUTED, anchor="middle")
f.save("failure-domains.svg")


# Figure 2-2: all critical request stages matter, not just API replica count.
f = Fig(760, 390)
f.text(380, 22, "支付确认 flow：任何串行必需阶段都可能成为共同故障", size=12, weight=700, color=NAVY, anchor="middle")
f.box(22, 91, 110, 54, "Client", ["付款请求"], "navy", title_size=9.6, size=8.2)
f.box(154, 91, 130, 54, "Identity", ["shared auth / token"], "purple", title_size=9.4, size=7.8)
f.box(308, 91, 135, 54, "Regional entry", ["zone-resilient endpoint"], "teal", title_size=9.2, size=7.5)
f.arrow((132, 118), (154, 118), color=NAVY)
f.arrow((284, 118), (308, 118), color=NAVY)
f.group(465, 44, 275, 202, "One region · API replicas", "plain", size=10.2)
for y, zone, style in ((83, "Zone 1 · outage", "red"), (137, "Zone 2", "teal"), (191, "Zone 3", "teal")):
    f.box(481, y, 242, 38, zone, ["API replica · health checked"], style, title_size=8.7, size=7.8)
    f.arrow((443, 118), (481, y + 19), color=GREEN)
f.box(48, 292, 235, 58, "Ledger write endpoint", ["zonal · only Zone 1", "required for payment commit"], "orange", title_size=9.6, size=8.1)
f.box(477, 292, 235, 58, "Business probe", ["write → read → reconcile", "not only VM / HTTP health"], "teal", title_size=9.6, size=8.1)
f.arrow((565, 246), (283, 320), color=RED, dash=True, label="ledger write", label_at=0.35, dy=-5, label_size=7.8)
f.arrow((283, 321), (477, 321), color=GREEN, label="verify result", dy=-7, label_size=7.8)
f.text(380, 375, "入口是否跨区须按实际 SKU 验证；本图的单 Zone ledger 会阻断 Zone 1 故障后的完整业务流。", size=8.8, color=MUTED, anchor="middle")
f.save("critical-flow.svg")


# Figure 2-3: translate business target into measurable signal and recovery gate.
f = Fig(760, 236)
f.text(380, 22, "从业务目标到恢复证据：SLO 指标与恢复门槛各有分母", size=12, weight=700, color=NAVY, anchor="middle")
f.box(24, 76, 156, 76, "Business flow", ["支付确认成功", "正确 + 可对账"], "navy", title_size=10.4, size=9)
f.box(210, 76, 156, 76, "SLI", ["成功请求比例 / 延迟", "用户视角测量规则"], "teal", title_size=10.4, size=9)
f.box(396, 76, 156, 76, "SLO + error budget", ["目标与统计窗口", "允许失败份额"], "orange", title_size=9.6, size=8.8)
f.box(582, 76, 156, 76, "Recovery gate", ["RTO + RPO", "数据与业务复验"], "green", title_size=10.2, size=9)
f.arrow((180, 114), (210, 114), color=NAVY)
f.arrow((366, 114), (396, 114), color=TEAL)
f.arrow((552, 114), (582, 114), color=ORANGE)
f.text(380, 194, "SLA 是供应方按条件作出的服务承诺；不能代替用户关键流 SLO，也不证明恢复完成。", size=9.5, color=RED, weight=600, anchor="middle")
f.text(380, 220, "分钟型 error budget 只适用于时间型 availability SLI；request-based SLI 按请求分母计算。", size=8.8, color=MUTED, anchor="middle")
f.save("reliability-targets.svg")
