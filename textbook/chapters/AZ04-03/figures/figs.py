"""Editable SVG mechanism diagrams for AZ04-03."""
from html import escape
from pathlib import Path

OUT = Path(__file__).parent
NAVY = "#17354c"
TEAL = "#008f95"
ORANGE = "#e9963e"
PURPLE = "#7356ba"
RED = "#d64a4a"
GREEN = "#287a54"
INK = "#233747"
MUTED = "#607585"
PANEL = "#f4f8fa"
LINE = "#b9cbd5"


def svg(title: str, width: int, height: int, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">
<title>{escape(title)}</title><rect width="100%" height="100%" rx="20" fill="white"/>
<style>text{{font-family:"Microsoft YaHei", "Noto Sans CJK SC", Arial, sans-serif;fill:{INK}}}.h{{font-size:24px;font-weight:700;fill:{NAVY}}}.sub{{font-size:17px;font-weight:700}}.body{{font-size:15px}}.small{{font-size:13px;fill:{MUTED}}}.tiny{{font-size:12px;fill:{MUTED}}}</style>
{body}</svg>'''


def text(x: int, y: int, value: str, cls: str = "body", anchor: str = "middle", color: str | None = None) -> str:
    fill = f' fill="{color}"' if color else ""
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}"{fill}>{escape(value)}</text>'


def box(x: int, y: int, w: int, h: int, label: str, lines: list[str], color: str, fill: str = "white") -> str:
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{color}" stroke-width="2"/>', text(x+w//2, y+30, label, "sub", color=color)]
    for i, line in enumerate(lines):
        out.append(text(x+w//2, y+58+i*23, line, "small"))
    return "\n".join(out)


def arrow(x1: int, y1: int, x2: int, y2: int, color: str, dash: bool = False) -> str:
    marker = {TEAL: "teal", ORANGE: "orange", PURPLE: "purple", RED: "red", GREEN: "green", NAVY: "navy"}.get(color, "navy")
    dash_attr = ' stroke-dasharray="7 6"' if dash else ""
    return f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="3"{dash_attr} marker-end="url(#{marker})"/>'


def defs() -> str:
    colors = {"navy": NAVY, "teal": TEAL, "orange": ORANGE, "purple": PURPLE, "red": RED, "green": GREEN}
    parts = ['<defs>']
    for name, color in colors.items():
        parts.append(f'<marker id="{name}" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0 L0 6 L9 3 z" fill="{color}"/></marker>')
    parts.append('</defs>')
    return "".join(parts)


def identity_pipeline() -> str:
    body = [defs(), text(650, 40, "先辨认调用者：控制面、node 和 Pod 不共用一个身份", "h")]
    body.append('<rect x="35" y="75" width="1230" height="385" rx="20" fill="#f7fafb" stroke="#9eb5c3" stroke-width="2"/>')
    body.append(text(650, 102, "AKS cluster resource", "sub"))
    body.append(box(70, 140, 325, 135, "Azure-managed control plane", ["API server · etcd · scheduler · controllers", "control-plane identity 管理关联 Azure 资源"], NAVY, "#edf2f7"))
    body.append(box(500, 140, 320, 135, "Node pool / VM", ["kubelet · container runtime", "kubelet identity 在 Pod 前拉取 image"], ORANGE, "#fff5e9"))
    body.append(box(925, 140, 285, 135, "Azure Container Registry", ["repository · tag/digest", "RBAC: AcrPull  |  ABAC: Repository Reader"], PURPLE, "#f4f0fb"))
    body.append(arrow(395, 205, 500, 205, NAVY))
    body.append(arrow(820, 205, 925, 205, ORANGE))
    body.append(text(870, 188, "image pull", "tiny"))
    body.append('<rect x="190" y="325" width="400" height="100" rx="14" fill="#eaf6f5" stroke="#078f91" stroke-width="2"/>')
    body.append(text(390, 354, "Pod workload identity", "sub", color=TEAL))
    body.append(text(390, 381, "projected ServiceAccount token + OIDC issuer", "small"))
    body.append(text(390, 402, "federated identity credential → Entra token", "small"))
    body.append('<rect x="760" y="325" width="380" height="100" rx="14" fill="#f1f7f3" stroke="#287a54" stroke-width="2"/>')
    body.append(text(950, 354, "Azure data-plane resource", "sub", color=GREEN))
    body.append(text(950, 383, "Key Vault / Storage / other API", "small"))
    body.append(text(950, 404, "target resource RBAC still applies", "small"))
    body.append(arrow(590, 374, 760, 374, TEAL))
    body.append(text(675, 357, "after container starts", "tiny"))
    body.append(text(650, 448, "No Azure identity is implied by Pod phase alone; ACR pull identity is not the application's data identity.", "small"))
    return svg("AKS control plane, kubelet image pull identity, and pod workload identity boundaries", 1300, 490, "\n".join(body))


def network_dns() -> str:
    body = [defs(), text(650, 40, "Overlay 地址、Service 发现和出站 NAT 是不同路径", "h")]
    body.append('<rect x="45" y="82" width="1210" height="340" rx="18" fill="#f7fafb" stroke="#9eb5c3" stroke-width="2"/>')
    body.append(text(200, 112, "VNet node subnet", "sub", color=NAVY))
    body.append(box(75, 150, 235, 110, "Node VM · node IP", ["kubelet + CNI", "VNet address"], NAVY, "#edf2f7"))
    body.append('<rect x="350" y="132" width="420" height="236" rx="16" fill="#f0f8f7" stroke="#008f95" stroke-width="2" stroke-dasharray="8 6"/>')
    body.append(text(560, 158, "Pod CIDR · Azure CNI Overlay", "sub", color=TEAL))
    body.append(box(375, 185, 165, 90, "Pod A", ["overlay IP", "app"], TEAL, "white"))
    body.append(box(580, 185, 165, 90, "Pod B", ["overlay IP", "service"], TEAL, "white"))
    body.append(box(470, 292, 180, 74, "Service ClusterIP", ["selector → ready endpoints"], PURPLE, "#f5f1fb"))
    body.append(arrow(540, 230, 580, 230, TEAL))
    body.append(arrow(560, 275, 560, 292, PURPLE))
    body.append(box(75, 300, 235, 70, "CoreDNS / LocalDNS", ["cluster.local → service", "external query → upstream"], PURPLE, "#f5f1fb"))
    body.append(arrow(375, 215, 310, 330, PURPLE))
    body.append(box(900, 147, 300, 95, "VNet / on-prem / internet", ["Pod egress SNAT uses node IP", "DNS, route, NSG and firewall still apply"], ORANGE, "#fff5e9"))
    body.append(arrow(745, 225, 900, 195, ORANGE))
    body.append(box(900, 290, 300, 80, "Ingress / LoadBalancer", ["external request enters service layer", "no direct inbound to overlay Pod IP"], GREEN, "#f0f7f2"))
    body.append(arrow(900, 320, 745, 245, GREEN))
    body.append(text(650, 402, "Keep pod CIDR, node VNet, Service CIDR and connected networks non-overlapping.", "small"))
    return svg("Azure CNI Overlay IP path and AKS CoreDNS service discovery", 1300, 440, "\n".join(body))


def scheduling_scaling() -> str:
    body = [defs(), text(650, 40, "先过滤硬约束，再比较 requests；扩 Pod 和扩 node 分属不同控制环", "h")]
    body.append(box(55, 120, 255, 150, "Pod request", ["CPU / memory requests", "nodeSelector / affinity", "tolerations / topology"], NAVY, "#edf2f7"))
    body.append(box(385, 120, 285, 150, "kube-scheduler", ["匹配 labels 与 tolerations", "扣除现有 Pod requests", "选择满足条件的 node"], TEAL, "#edf8f7"))
    body.append(box(755, 90, 220, 110, "可用 node", ["requests 能放下", "Pod → Bound"], GREEN, "#f1f7f2"))
    body.append(box(755, 230, 220, 130, "无 node 可放", ["Pod → Pending", "Events 说明失败约束"], RED, "#fbf1f1"))
    body.append(box(1050, 105, 205, 110, "HPA", ["按指标调整 Pod 副本数", "改变期望工作负载"], PURPLE, "#f5f1fb"))
    body.append(box(1050, 250, 205, 110, "Cluster Autoscaler", ["看无法调度的 Pod", "在 min/max 与可行池内扩 node"], ORANGE, "#fff5e9"))
    body.append(arrow(310, 190, 385, 190, NAVY))
    body.append(arrow(670, 160, 755, 145, GREEN))
    body.append(arrow(670, 225, 755, 285, RED))
    body.append(arrow(975, 285, 1050, 305, ORANGE))
    body.append(arrow(1150, 250, 1150, 215, PURPLE))
    body.append(text(1150, 235, "副本需求", "tiny"))
    body.append(text(650, 400, "如果 selector / taint / node规格本身不兼容，增加 max-count 不会使该 Pod 可调度。", "small"))
    return svg("Kubernetes scheduling resource requests, HPA and AKS cluster autoscaler", 1300, 430, "\n".join(body))


def readiness_upgrade() -> str:
    body = [defs(), text(650, 40, "Pod 何时接流量，与 node 何时可被安全 drain，是两组健康门", "h")]
    body.append(text(650, 105, "Pod lifecycle → Service eligibility", "sub", color=NAVY))
    body.append(box(60, 145, 205, 100, "Image pull", ["kubelet identity", "registry + network"], ORANGE, "#fff5e9"))
    body.append(box(325, 145, 205, 100, "Startup probe", ["启动保护", "通过后启动其他 probes"], PURPLE, "#f5f1fb"))
    body.append(box(590, 145, 205, 100, "Readiness", ["决定 Pod Ready", "影响 Service endpoints"], TEAL, "#f0f8f7"))
    body.append(box(855, 145, 205, 100, "Service", ["selector + Ready Pod", "可用 endpoint"], GREEN, "#f1f7f2"))
    body.append(box(1120, 145, 145, 100, "Request", ["路径与 SLI", "仍需验证"], NAVY, "#edf2f7"))
    body.append(arrow(265, 195, 325, 195, ORANGE))
    body.append(arrow(530, 195, 590, 195, PURPLE))
    body.append(arrow(795, 195, 855, 195, TEAL))
    body.append(arrow(1060, 195, 1120, 195, GREEN))
    body.append('<path d="M692 245 L692 290 L405 290" fill="none" stroke="#d64a4a" stroke-width="3" marker-end="url(#red)"/>')
    body.append(text(550, 280, "Liveness 失败 → 重启容器；不替代业务依赖验证", "small", color=RED))
    body.append(text(650, 350, "Node-pool upgrade → surge node → PDB 允许驱逐 → drain/升级 → workload Ready", "sub", color=NAVY))
    body.append(box(190, 380, 270, 80, "Surge capacity", ["额外 VM / IP / quota / SKU"], ORANGE, "#fff5e9"))
    body.append(box(515, 380, 270, 80, "PDB", ["约束自愿 eviction 的可用副本"], RED, "#fbf1f1"))
    body.append(box(840, 380, 270, 80, "Drain and upgrade", ["版本策略 + workload 验证"], TEAL, "#f0f8f7"))
    body.append(arrow(460, 420, 515, 420, ORANGE))
    body.append(arrow(785, 420, 840, 420, RED))
    return svg("AKS startup readiness liveness Service endpoints and node pool upgrade PDB", 1300, 485, "\n".join(body))


def upgrade_flow() -> str:
    body = [defs(), text(650, 40, "Node-pool upgrade 是容量、驱逐预算和版本状态的协调操作", "h")]
    body.append(box(45, 135, 220, 125, "1 · Validate target", ["当前 support plan / region", "control plane 与 pool skew", "release notes / APIs"], NAVY, "#edf2f7"))
    body.append(box(315, 135, 220, 125, "2 · Prepare capacity", ["maxSurge / maxUnavailable", "VM quota · SKU · subnet IP", "临时容量可用"], ORANGE, "#fff5e9"))
    body.append(box(585, 135, 220, 125, "3 · Eviction gate", ["cordon + drain", "PDB 允许副本数", "workload 可重调度"], RED, "#fbf1f1"))
    body.append(box(855, 135, 190, 125, "4 · Replace", ["更新 node image / kubelet", "node 返回 Ready"], TEAL, "#f0f8f7"))
    body.append(box(1090, 135, 175, 125, "5 · Verify", ["Pod Ready", "EndpointSlice", "request path / SLI"], GREEN, "#f1f7f2"))
    body.append(arrow(265, 198, 315, 198, NAVY))
    body.append(arrow(535, 198, 585, 198, ORANGE))
    body.append(arrow(805, 198, 855, 198, RED))
    body.append(arrow(1045, 198, 1090, 198, TEAL))
    body.append('<rect x="105" y="330" width="470" height="85" rx="14" fill="#fff5e9" stroke="#e9963e" stroke-width="2"/>')
    body.append(text(340, 360, "Capacity gate fails", "sub", color=ORANGE))
    body.append(text(340, 388, "quota / address / SKU shortage → add capacity or reschedule", "small"))
    body.append('<rect x="725" y="330" width="470" height="85" rx="14" fill="#fbf1f1" stroke="#d64a4a" stroke-width="2"/>')
    body.append(text(960, 360, "Disruption gate fails", "sub", color=RED))
    body.append(text(960, 388, "PDB forbids eviction → restore Ready replicas or repair the budget", "small"))
    body.append('<path d="M420 260 L420 330" fill="none" stroke="#e9963e" stroke-width="3" marker-end="url(#orange)"/>')
    body.append('<path d="M695 260 L695 310 L960 310 L960 330" fill="none" stroke="#d64a4a" stroke-width="3" marker-end="url(#red)"/>')
    body.append(text(650, 465, "A successful control-plane upgrade must still be followed by workload and traffic verification.", "small"))
    return svg("AKS node pool upgrade sequence and surge capacity and PDB gates", 1300, 490, "\n".join(body))


if __name__ == "__main__":
    figures = {
        "identity-pipeline.svg": identity_pipeline(),
        "network-dns.svg": network_dns(),
        "scheduling-scaling.svg": scheduling_scaling(),
        "readiness-upgrade.svg": readiness_upgrade(),
        "upgrade-flow.svg": upgrade_flow(),
    }
    for name, data in figures.items():
        (OUT / name).write_text(data, encoding="utf-8")
        print(f"wrote {name}")
