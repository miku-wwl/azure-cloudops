"""Generate original, editable SVG figures for AZ05-03."""

from __future__ import annotations

from html import escape
from pathlib import Path

OUT = Path(__file__).parent
NAVY = "#17324d"
TEAL = "#087f8c"
PALE = "#edf5f7"
BLUE = "#eaf1f8"
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
WHITE = "#ffffff"


def t(x: int, y: int, value: str, size: int = 20, color: str = INK,
      weight: int = 400, anchor: str = "middle") -> str:
    return (f'<text x="{x}" y="{y}" font-family="Aptos,Arial,sans-serif" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="{anchor}">{escape(value)}</text>')


def box(x: int, y: int, w: int, h: int, title: str, lines: list[str],
        stroke: str = NAVY, fill: str = WHITE, size: int = 17) -> str:
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" '
           f'fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>',
           t(x + w // 2, y + 33, title, 21, stroke, 700)]
    for i, line in enumerate(lines):
        out.append(t(x + w // 2, y + 65 + i * 25, line, size))
    return "\n".join(out)


def start(title: str, subtitle: str, width: int = 1200, height: int = 560) -> list[str]:
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="#ffffff"/>',
            t(34, 42, title, 27, NAVY, 700, "start"),
            t(34, 75, subtitle, 17, MUTED, 400, "start")]


def arrow(x1: int, y1: int, x2: int, y2: int, color: str = NAVY,
          dashed: bool = False) -> str:
    dash = ' stroke-dasharray="9 7"' if dashed else ""
    return (f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" '
            f'stroke-width="3"{dash} marker-end="url(#arrow)"/>')


def finish(parts: list[str], filename: str) -> None:
    parts.insert(1, f'<defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="5" orient="auto"><path d="M0,0 L0,10 L11,5 z" fill="{NAVY}"/></marker></defs>')
    parts.append("</svg>")
    (OUT / filename).write_text("\n".join(parts), encoding="utf-8")


def scope_boundary() -> None:
    p = start("资源可见范围是一组边界的交集",
              "身份上下文、显式 scope 和资源级读取权限共同决定返回的数据", 1200, 560)
    p.extend([
        box(38, 154, 210, 132, "Identity", ["principal + tenant", "CLI / Az context"], PURPLE, LAVENDER),
        box(285, 154, 210, 132, "Subscription scope", ["approved ID list", "or management group"], TEAL, PALE),
        box(532, 154, 210, 132, "RBAC read", ["permitted objects", "others not returned"], ORANGE, SAND),
        box(779, 154, 180, 132, "ARG index", ["current indexed", "resource state"], NAVY, BLUE),
        box(996, 154, 168, 132, "Result", ["visible subset", "not tenant truth"], RED, ROSE),
        arrow(248, 220, 275, 220), arrow(495, 220, 522, 220), arrow(742, 220, 769, 220), arrow(959, 220, 986, 220),
        box(214, 358, 320, 86, "Missing subscription", ["context or scope may omit it"], RED, ROSE, 16),
        box(666, 358, 320, 86, "Missing object", ["read permission may hide it"], ORANGE, SAND, 16),
        arrow(390, 286, 374, 348, RED, True), arrow(636, 286, 820, 348, ORANGE, True),
        t(600, 510, "“查询成功”说明请求完成；范围完整仍需身份、授权和 scope 证据。", 19, NAVY, 700),
    ])
    finish(p, "scope-boundary.svg")


def tool_paths() -> None:
    p = start("命令行工具的相似外观，背后是不同查询路径",
              "ARM 资源列表直接调用 Resource Manager；Resource Graph 以索引和 KQL 扩展探索", 1200, 560)
    p.extend([
        box(44, 138, 280, 112, "Azure CLI / Az PowerShell", ["identity + selected context", "explicit subscription ID"], PURPLE, LAVENDER),
        box(468, 112, 270, 110, "Direct ARM list", ["az resource list", "Get-AzResource"], TEAL, PALE),
        box(468, 290, 270, 110, "Resource Graph", ["az graph query", "Search-AzGraph · KQL"], ORANGE, SAND),
        box(860, 112, 278, 110, "Per-subscription result", ["ARM response", "JMESPath / PowerShell"], GREEN, MINT),
        box(860, 290, 278, 110, "Cross-scope exploration", ["indexed properties", "KQL filter / project / join"], NAVY, BLUE),
        arrow(324, 184, 458, 166, TEAL), arrow(324, 206, 458, 344, ORANGE),
        arrow(738, 166, 850, 166, GREEN), arrow(738, 344, 850, 344, NAVY),
        t(600, 466, "CLI `--query` = JMESPath　 ·　 Resource Graph `-q` / `-Query` = KQL", 18, RED, 700),
        t(600, 506, "Resource Graph 索引有短暂延迟；它不是每次都同步读取每个 resource provider。", 17, MUTED),
    ])
    finish(p, "tool-paths.svg")


def query_pipeline() -> None:
    p = start("让查询文本表达 scope 和清单结构",
              "显式 subscription 集合 → 必要列 → 唯一键排序 → 受控分页", 1200, 560)
    p.extend([
        box(42, 165, 210, 126, "1 · Scope", ["approved IDs", "tenant + identity"], PURPLE, LAVENDER),
        box(286, 165, 210, 126, "2 · Filter", ["type / location", "only if required"], TEAL, PALE),
        box(530, 165, 210, 126, "3 · Project", ["id + subscriptionId", "name + type"], ORANGE, SAND),
        box(774, 165, 180, 126, "4 · Order", ["id asc", "unique stable key"], GREEN, MINT),
        box(988, 165, 174, 126, "5 · Page", ["first ≤ 1,000", "check next token"], NAVY, BLUE),
        arrow(252, 228, 276, 228), arrow(496, 228, 520, 228), arrow(740, 228, 764, 228), arrow(954, 228, 978, 228),
        box(205, 356, 320, 84, "Truncate before paging", ["take / limit / sample"], RED, ROSE, 16),
        box(674, 356, 320, 84, "Sort on repeated values", ["location / name only"], RED, ROSE, 16),
        arrow(355, 291, 365, 346, RED, True), arrow(864, 291, 834, 346, RED, True),
        t(600, 504, "保留 id 标量列；按唯一 id 排序；不要把单页行数当成总数。", 19, NAVY, 700),
    ])
    finish(p, "query-pipeline.svg")


def pagination() -> None:
    p = start("稳定排序帮助重放分页，但不能冻结资源集合",
              "续页请求需要检查 token、结果数和 ID；资源在请求间变化时 offset 仍可能移动", 1200, 600)
    p.extend([
        t(168, 137, "静态资源集合", 19, NAVY, 700),
        *[box(48 + i * 180, 166, 150, 78, f"id-{i+1:02d}", ["unique key"], TEAL if i < 3 else GREEN, PALE if i < 3 else MINT, 15) for i in range(6)],
        t(600, 287, "order by id asc → page 1 → continuation token → page 2", 18, GREEN, 700),
        arrow(205, 260, 205, 316, GREEN), arrow(385, 260, 385, 316, GREEN), arrow(565, 260, 565, 316, GREEN),
        box(72, 360, 360, 98, "Between requests: delete id-02", ["offset positions shift"], ORANGE, SAND),
        box(510, 360, 300, 98, "Page 1", ["id-01 · id-02"], TEAL, PALE),
        box(870, 360, 280, 98, "Next offset page", ["id-04 · id-05"], RED, ROSE),
        arrow(432, 408, 500, 408, ORANGE), arrow(810, 408, 860, 408, RED),
        t(600, 520, "id-03 可能被跳过。稳定 ID 排序提高可重复性，但不是跨页事务快照。", 19, RED, 700),
        t(600, 559, "若仍有续页 token，继续读取；收尾时核对去重 ID、页数和查询时间。", 17, MUTED),
    ])
    finish(p, "pagination.svg")


def completeness_checks() -> None:
    p = start("资产清单的完整性要分别通过五项检查",
              "任何一项未知，都应把结论限定在已验证的 principal、scope 和读取时间", 1200, 590)
    checks = [
        (74, "Scope", "tenant + subscription IDs", PURPLE, LAVENDER),
        (292, "RBAC", "read visibility", TEAL, PALE),
        (510, "Freshness", "index lag + query time", ORANGE, SAND),
        (728, "Pagination", "all pages + token", GREEN, MINT),
        (946, "Repeatability", "unique id + drift", NAVY, BLUE),
    ]
    for x, title, line, stroke, fill in checks:
        p.append(box(x, 178, 180, 112, title, [line], stroke, fill, 15))
        p.append(arrow(x + 90, 290, 600, 372, stroke, True))
    p.extend([
        box(330, 372, 540, 110, "Evidence-backed inventory claim", ["query version · scope manifest · timestamps", "page count · unique IDs · duplicates · exceptions"], NAVY, BLUE, 17),
        t(600, 540, "没有独立的范围清单和权限证据时，“没有返回”不等于“资源不存在”。", 18, RED, 700),
    ])
    finish(p, "completeness-checks.svg")


if __name__ == "__main__":
    scope_boundary()
    tool_paths()
    query_pipeline()
    pagination()
    completeness_checks()
