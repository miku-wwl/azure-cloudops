"""Original mechanism figures for AZ04-01."""

from figlib import Fig, NAVY, TEAL, ORANGE, RED, GREEN, PURPLE, MUTED


# Figure 10-1: independent state and evidence planes.
f = Fig(760, 430)
f.text(380, 22, "一台 VM 是多个独立观察面，不是一个总健康状态", size=12, weight=700, color=NAVY, anchor="middle")
f.box(22, 56, 166, 91, "Power state", ["Instance View", "Running / Stopped", "Allocated / Deallocated"], "navy", title_size=9.6, size=8.0, lh=14)
f.box(208, 56, 166, 91, "Provisioning state", ["最近控制面操作", "Succeeded / Failed", "可与 Running 并存"], "orange", title_size=9.6, size=8.0, lh=14)
f.box(394, 56, 166, 91, "Guest / application", ["OS、agent、进程", "应用 endpoint probe", "需各自配置观察"], "teal", title_size=9.6, size=8.0, lh=14)
f.box(580, 56, 158, 91, "Compute billing", ["按 power state", "Stopped (Allocated)", "仍计 VM usage"], "red", title_size=9.4, size=7.8, lh=14)
f.text(380, 177, "相互独立：一个观察面不会自动证明另一个观察面的健康", size=9.1, weight=700, color=RED, anchor="middle")
f.line(32, 198, 728, 198, color="#d5dde3", sw=1)
f.box(30, 222, 211, 116, "Host observation", ["平台 host metrics 默认收集", "boot diagnostics：启动屏幕", "与串口日志"], "gray", title_size=9.5, size=8.0, lh=15)
f.box(274, 222, 211, 116, "Guest observation", ["AMA + DCR 获取已配置的", "guest metrics / logs", "不配置时不能从空白推断"], "purple", title_size=9.5, size=8.0, lh=15)
f.box(518, 222, 211, 116, "Application observation", ["Health Extension / probe", "只判断被配置的 endpoint", "不等于完整业务 SLI"], "green", title_size=9.5, size=8.0, lh=15)
f.arrow((135, 338), (135, 373), color=MUTED, dash=True)
f.arrow((380, 338), (380, 373), color=MUTED, dash=True)
f.arrow((623, 338), (623, 373), color=MUTED, dash=True)
f.text(380, 399, "每条证据都有来源与边界；先匹配症状，再选择下一条观察", size=8.6, color=MUTED, anchor="middle")
f.save("state-vector.svg")


# Figure 10-2: scale-set model versus instance versions and rollout.
f = Fig(760, 420)
f.text(380, 22, "VMSS model 改动不会自动等于每个实例已更新", size=12, weight=700, color=NAVY, anchor="middle")
f.box(20, 64, 152, 82, "创建时选模式", ["Uniform：成组 / 同质", "Flexible：标准 VM 管理"], "navy", title_size=9.4, size=7.9, lh=14)
f.box(202, 64, 154, 82, "Scale-set model", ["v4 → v5", "声明的期望配置"], "teal", title_size=9.4, size=8.2, lh=14)
f.arrow((172, 105), (202, 105), color=NAVY)
f.text(372, 45, "upgrade policy 选择推进路径", size=7.8, color=MUTED, anchor="middle")
f.box(400, 42, 150, 70, "Manual", ["现有实例等显式更新", "新实例使用 v5"], "orange", title_size=9.3, size=7.7, lh=13)
f.box(400, 126, 150, 70, "Automatic", ["不保证实例顺序", "可能同时影响多台"], "red", title_size=9.3, size=7.7, lh=13)
f.box(400, 210, 150, 86, "Rolling", ["按批次推进实例", "由 health signal 控制门槛", "具体组合需核对支持矩阵"], "green", title_size=9.3, size=7.5, lh=13)
f.arrow((356, 80), (400, 77), color=ORANGE, sw=1.4)
f.arrow((356, 105), (400, 161), color=RED, sw=1.4)
f.arrow((356, 129), (400, 253), color=GREEN, sw=1.4)
f.box(580, 210, 158, 86, "Application health", ["Flexible：Extension", "Uniform：Extension / LB probe", "与 PowerState 分开"], "purple", title_size=9.0, size=7.2, lh=13)
f.arrow((550, 253), (580, 253), color=PURPLE, label="probe", dy=-8, label_size=7.4)
f.note(30, 321, 700, 74, ["图示解释模型和实例版本，不保证任意 mode/API 组合均支持相同策略。", "部署前核对 orchestration、API、upgrade policy 与 health configuration。"], style="orange", size=8.0, title="Source boundary")
f.save("vmss-rollout.svg")


# Figure 10-3: single uncached disk I/O ceilings.
f = Fig(760, 382)
f.text(380, 22, "单盘 uncached 路径：请求同时受 disk cap 与 VM cap 约束", size=12, weight=700, color=NAVY, anchor="middle")
f.box(20, 91, 145, 91, "Application demand", ["9,000 IOPS", "示例输入"], "gray", title_size=9.3, size=8.4, lh=15)
f.box(218, 64, 205, 108, "Managed Disk limit", ["5,000 IOPS", "请求 > disk cap"], "red", title_size=9.6, size=8.5, lh=15)
f.box(218, 211, 205, 108, "VM uncached limit", ["8,000 IOPS", "请求 > VM cap"], "orange", title_size=9.6, size=8.5, lh=15)
f.box(504, 122, 219, 114, "Delivered ceiling", ["min(request, disk, VM)", "5,000 IOPS in this fixture", "不是 SKU 性能保证"], "teal", title_size=9.7, size=8.4, lh=15)
f.arrow((165, 130), (218, 118), color=RED, label="远端 I/O", dy=-8, label_size=7.7)
f.arrow((165, 149), (218, 260), color=ORANGE, label="同一请求受 VM 预算", dx=7, dy=3, label_size=7.4)
f.arrow((423, 118), (504, 156), color=RED, label="较小 disk cap 成瓶颈", dy=-7, label_size=7.4)
f.arrow((423, 265), (504, 201), color=ORANGE, label="较大 VM cap 未先触顶", dy=11, label_size=7.2)
f.text(380, 355, "Host cache 会改变 I/O path；多盘总额、burst、队列不在此单盘教学模型内。", size=8.1, color=MUTED, anchor="middle")
f.save("io-ceilings.svg")
