"""Original AZ02-02 NSG, ASG and diagnostic mechanism diagrams."""

from figlib import Fig, NAVY, TEAL, ORANGE, RED, GREEN, MUTED


# Figure 4-1: a lower numeric priority is evaluated first; first match stops.
f = Fig(760, 326)
f.text(380, 22, "NSG 按优先级从小到大匹配五元组；命中第一条规则后停止", size=12, weight=700, color=NAVY, anchor="middle")
f.group(24, 48, 440, 228, "pay-api-01 inbound / TCP 8443", "plain", size=10.2)
f.box(42, 82, 402, 42, "100 · Deny-Maintenance-Api-Port", ["Source Any → ASG-Pay-API · Deny"], "red", title_size=9.5, size=8.3)
f.box(42, 135, 402, 42, "110 · Allow-Edge-To-Api", ["ASG-Edge → ASG-Pay-API · Allow"], "green", title_size=9.5, size=8.3)
f.box(42, 188, 402, 42, "120 · Deny-Other-To-Api", ["Any → ASG-Pay-API · Deny"], "orange", title_size=9.5, size=8.3)
f.box(42, 241, 402, 26, "65500 · DenyAllInbound (Azure default)", [], "gray", title_size=8.5)
f.box(495, 95, 236, 74, "Edge packet", ["10.40.1.20:53144", "→ 10.40.2.10:8443"], "navy", title_size=10, size=8.7)
f.arrow((495, 132), (444, 103), color=RED, label="matches 100", dx=16, dy=-5, label_size=8)
f.box(501, 198, 224, 55, "Result: DENY", ["Rule 110 is never reached"], "red", title_size=10, size=8.7)
f.arrow((613, 169), (613, 198), color=RED)
f.text(380, 303, "Priority 100 is earlier than 110; “higher priority” means a smaller number, not a larger one.", size=9.1, color=MUTED, anchor="middle")
f.save("rule-priority.svg")


# Figure 4-2: subnet and NIC scopes are independent filtering layers; ASGs target NIC roles.
f = Fig(760, 332)
f.text(380, 22, "同一入站流量要通过 subnet NSG 与 NIC NSG；ASG 表示 NIC 角色", size=12, weight=700, color=NAVY, anchor="middle")
f.box(24, 112, 126, 64, "Edge proxy", ["NIC ∈ ASG-Edge", "10.40.1.20"], "navy", title_size=9.4, size=8.2)
f.box(190, 75, 198, 138, "Subnet NSG", ["110 Allow Edge → API", "120 Deny other → API", "Both rules use TCP 8443"], "green", title_size=10, size=8.5)
f.box(438, 75, 198, 138, "NIC NSG", ["100 Deny maintenance", "110 Allow Edge → API", "First matching rule wins"], "red", title_size=10, size=8.5)
f.box(684, 112, 60, 64, "API", ["ASG-API"], "teal", title_size=9.2, size=7.6)
f.arrow((150, 137), (190, 137), color=GREEN, label="allow", dy=-8, label_size=8)
f.arrow((388, 137), (438, 137), color=GREEN, label="allow", dy=-8, label_size=8)
f.arrow((636, 137), (684, 137), color=RED, label="deny", dy=-9, label_size=7.8)
f.box(86, 244, 588, 52, "Effective view", ["Inspect the rules at both scopes; priority 110 in one NSG does not cancel priority 100 in another."], "orange", title_size=9.6, size=8.6)
f.text(380, 322, "ASG membership is on NICs; ASGs in one NSG rule must fit the documented same-VNet constraint.", size=8.8, color=MUTED, anchor="middle")
f.save("nsg-asg-scope.svg")


# Figure 4-3: statefulness, rule evaluation and active connectivity tests prove different things.
f = Fig(760, 350)
f.text(380, 22, "已建立连接有 flow state；过滤诊断与端到端探测回答不同问题", size=12, weight=700, color=NAVY, anchor="middle")
f.box(22, 74, 155, 62, "Outbound request", ["New 5-tuple", "must match NSGs"], "navy", title_size=9.4, size=8.4)
f.box(217, 74, 153, 62, "Flow record", ["Connection state", "remembered"], "teal", title_size=9.4, size=8.4)
f.box(410, 74, 153, 62, "Response packet", ["Established reverse", "flow is allowed"], "green", title_size=9.4, size=8.4)
f.box(603, 74, 135, 62, "New connection", ["Current rules", "are evaluated"], "orange", title_size=9.2, size=8.2)
f.arrow((177, 105), (217, 105), color=NAVY)
f.arrow((370, 105), (410, 105), color=GREEN)
f.arrow((563, 105), (603, 105), color=ORANGE)
f.text(380, 168, "Removing an allow rule does not terminate an existing connection; test with a new flow when validating a rule change.", size=8.9, color=RED, anchor="middle")
f.box(25, 208, 215, 88, "Effective NSG", ["What subnet + NIC rules apply?", "VM must be running for CLI view"], "navy", title_size=9.7, size=8.3)
f.box(272, 208, 215, 88, "IP Flow Verify", ["Would TCP / UDP packet be", "allowed? Which rule matched?"], "teal", title_size=9.7, size=8.3)
f.box(519, 208, 219, 88, "Connection Troubleshoot", ["Can a probe connect? Check", "route, NSG, DNS, listener, hops"], "orange", title_size=9.3, size=8.2)
f.arrow((240, 252), (272, 252), color=MUTED)
f.arrow((487, 252), (519, 252), color=MUTED)
f.text(380, 329, "IP Flow Verify is not TCP reachability; Connection Troubleshoot sends active probes and has a broader diagnostic scope.", size=8.7, color=MUTED, anchor="middle")
f.save("stateful-diagnostics.svg")
