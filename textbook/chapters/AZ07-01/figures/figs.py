"""Create five original, editable mechanism diagrams for AZ07-01."""

from __future__ import annotations

from html import escape
from pathlib import Path

OUT = Path(__file__).parent
NAVY = "#17324d"
TEAL = "#087f8c"
BLUE = "#eaf1f8"
PALE = "#edf5f7"
ORANGE = "#c96a18"
SAND = "#fff3e5"
GREEN = "#23764d"
MINT = "#eaf6ef"
PURPLE = "#684bb1"
LAVENDER = "#f2edfb"
RED = "#aa4052"
ROSE = "#fff0f1"
INK = "#273b4d"
MUTED = "#5d7183"


def text(x: int, y: int, value: str, size: int = 19, color: str = INK,
         weight: int = 400, anchor: str = "middle") -> str:
    return (f'<text x="{x}" y="{y}" font-family="Aptos,Arial,sans-serif" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="{anchor}">{escape(value)}</text>')


def box(x: int, y: int, w: int, h: int, title: str, lines: list[str],
        stroke: str = NAVY, fill: str = "#ffffff", size: int = 17) -> str:
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="15" '
             f'fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>',
             text(x + w // 2, y + 34, title, 21, stroke, 700)]
    for i, line in enumerate(lines):
        parts.append(text(x + w // 2, y + 67 + i * 25, line, size))
    return "\n".join(parts)


def arrow(x1: int, y1: int, x2: int, y2: int, color: str = NAVY,
          dashed: bool = False) -> str:
    dash = ' stroke-dasharray="9 7"' if dashed else ""
    return (f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" '
            f'stroke-width="3"{dash} marker-end="url(#arrow)"/>')


def start(title: str, subtitle: str, width: int = 1200, height: int = 560) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="5" orient="auto"><path d="M0,0 L0,10 L11,5 z" fill="#17324d"/></marker></defs>',
        text(34, 42, title, 27, NAVY, 700, "start"),
        text(34, 75, subtitle, 17, MUTED, 400, "start"),
    ]


def finish(parts: list[str], filename: str) -> None:
    parts.append("</svg>")
    (OUT / filename).write_text("\n".join(parts), encoding="utf-8")


def core_provider_arm() -> None:
    p = start("三层机制：语言与计划、Terraform Provider、ARM Resource Provider",
              "同叫 Provider 的组件不处在同一层；每层回答不同问题", 1200, 480)
    p.extend([
        box(55, 139, 310, 152, "Terraform Core", ["HCL · modules · dependency graph", "State address · Plan · lifecycle"], NAVY, BLUE, 17),
        box(445, 139, 310, 152, "Terraform Provider plugin", ["AzureRM: typed resource schema", "AzAPI: ARM REST API + version/body"], TEAL, PALE, 17),
        box(835, 139, 310, 152, "Azure ARM service", ["Microsoft.Storage / Network / ...", "API namespace and remote resource"], ORANGE, SAND, 17),
        arrow(365, 210, 435, 210, NAVY),
        arrow(755, 210, 825, 210, TEAL),
        text(600, 355, "Core plans an address; a Terraform Provider maps it to ARM operations.", 20, NAVY, 700),
        text(600, 398, "Azure Resource Provider is an ARM service namespace, not a Terraform plugin.", 18, MUTED),
    ])
    finish(p, "core-provider-arm.svg")


def dependency_dag() -> None:
    p = start("引用表达排序；无关节点可以并行", "以资源属性引用形成隐式边；depends_on 只补隐藏依赖", 1200, 560)
    p.extend([
        box(56, 185, 220, 110, "Virtual network", ["output: id"], PURPLE, LAVENDER),
        box(354, 119, 230, 110, "Subnet A", ["reads VNet id"], TEAL, PALE),
        box(354, 342, 230, 110, "Subnet B", ["reads VNet id"], TEAL, PALE),
        box(676, 185, 230, 110, "Private endpoint", ["reads subnet id"], ORANGE, SAND),
        box(954, 185, 205, 110, "DNS zone group", ["reads endpoint id"], GREEN, MINT),
        arrow(276, 220, 344, 176, PURPLE), arrow(276, 261, 344, 392, PURPLE),
        arrow(584, 176, 666, 220, TEAL), arrow(906, 240, 944, 240, ORANGE),
        text(470, 509, "Subnet A 与 Subnet B 可并行；私有终结点等待 Subnet A。", 19, NAVY, 700),
    ])
    finish(p, "dependency-dag.svg")


def state_address_binding() -> None:
    p = start("State 保存地址到远端对象的绑定", "读取当前对象后，漂移才会进入计划差异", 1200, 520)
    p.extend([
        box(58, 166, 298, 126, "Configuration address", ["azurerm_storage_account.logs", "desired fields + provider"], PURPLE, LAVENDER),
        box(450, 166, 298, 126, "Terraform State", ["address → provider + remote ID", "one remote object, one address"], NAVY, BLUE),
        box(842, 166, 298, 126, "Azure remote object", ["ARM ID + observed attributes", "manual drift may exist"], TEAL, PALE),
        arrow(356, 228, 440, 228, PURPLE),
        arrow(748, 228, 832, 228, TEAL),
        arrow(842, 277, 748, 318, ORANGE, True),
        text(598, 371, "Provider refresh → compare with configuration → proposed change", 19, ORANGE, 700),
        text(600, 440, "State 是绑定与元数据；不是配置，也不是云资源本身。", 18, MUTED),
    ])
    finish(p, "state-address-binding.svg")


def plan_review() -> None:
    p = start("Plan 产出动作提案；审阅范围与破坏性", "云端 Plan 会通过 Provider 观察远端状态；validate 不做这件事", 1200, 565)
    p.extend([
        box(46, 166, 224, 124, "Config + State", ["addresses · inputs", "provider lock · backend"], PURPLE, LAVENDER),
        box(342, 166, 230, 124, "Provider read", ["remote refresh", "version-specific behavior"], TEAL, PALE),
        box(644, 166, 230, 124, "Plan actions", ["create · update", "replace · destroy"], ORANGE, SAND),
        box(946, 166, 210, 124, "Review gates", ["scope · ID · drift", "data · rollback"], GREEN, MINT),
        arrow(270, 228, 332, 228, PURPLE), arrow(572, 228, 634, 228, TEAL), arrow(874, 228, 936, 228, ORANGE),
        box(232, 365, 300, 91, "validate", ["syntax + internal consistency"], NAVY, BLUE, 16),
        box(668, 365, 300, 91, "business probe", ["service + data invariants"], GREEN, MINT, 16),
        text(600, 513, "Provider registration and other initialization behavior depend on the locked provider version and configuration.", 17, RED, 700),
    ])
    finish(p, "plan-review.svg")


def import_lifecycle() -> None:
    p = start("Import 接管 State 绑定，不创建远端资源", "先写目标配置，再审阅 import plan 与后续配置差异", 1200, 570)
    p.extend([
        box(44, 172, 216, 126, "Existing ARM object", ["resource already exists", "verify exact provider ID"], ORANGE, SAND),
        box(334, 105, 270, 126, "Resource configuration", ["destination address", "attributes match intent"], PURPLE, LAVENDER),
        box(334, 320, 270, 126, "Import declaration", ["to = destination address", "id = provider-defined ID"], TEAL, PALE),
        box(698, 172, 205, 126, "Review plan", ["import action", "no surprise changes"], NAVY, BLUE),
        box(988, 172, 175, 126, "State binding", ["one address", "one remote ID"], GREEN, MINT),
        arrow(260, 220, 324, 167, ORANGE), arrow(260, 254, 324, 376, ORANGE),
        arrow(604, 168, 688, 208, PURPLE), arrow(604, 382, 688, 253, TEAL),
        arrow(903, 235, 978, 235, NAVY),
        text(600, 516, "导入后仍要 reconcile 配置；资源类型迁移需要单独的 State 计划。", 18, RED, 700),
    ])
    finish(p, "import-lifecycle.svg")


if __name__ == "__main__":
    core_provider_arm()
    dependency_dag()
    state_address_binding()
    plan_review()
    import_lifecycle()
