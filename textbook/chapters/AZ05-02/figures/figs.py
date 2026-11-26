"""Generate original, editable SVG figures for AZ05-02."""

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


def text(x: int, y: int, value: str, size: int = 21, color: str = INK,
         weight: int = 400, anchor: str = "middle") -> str:
    return (f'<text x="{x}" y="{y}" font-family="Aptos,Arial,sans-serif" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="{anchor}">{escape(value)}</text>')


def box(x: int, y: int, w: int, h: int, title: str, lines: list[str],
        stroke: str = NAVY, fill: str = WHITE, size: int = 18) -> str:
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="17" '
           f'fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>',
           text(x + w // 2, y + 34, title, 21, stroke, 700)]
    for i, line in enumerate(lines):
        out.append(text(x + w // 2, y + 67 + i * 26, line, size))
    return "\n".join(out)


def start(title: str, subtitle: str, width: int = 1200, height: int = 540) -> list[str]:
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="#ffffff"/>',
            text(34, 42, title, 27, NAVY, 700, "start"),
            text(34, 74, subtitle, 17, MUTED, 400, "start")]


def arrow(x1: int, y1: int, x2: int, y2: int, color: str = NAVY,
          dashed: bool = False) -> str:
    dash = ' stroke-dasharray="9 7"' if dashed else ""
    return (f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" '
            f'stroke-width="3"{dash} marker-end="url(#arrow)"/>')


def finish(parts: list[str], filename: str) -> None:
    parts.insert(1, f'<defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="5" orient="auto"><path d="M0,0 L0,10 L11,5 z" fill="{NAVY}"/></marker></defs>')
    parts.append("</svg>")
    (OUT / filename).write_text("\n".join(parts), encoding="utf-8")


def data_path() -> None:
    p = start("先确认数据如何进入工作区，再决定从哪张表开始查",
              "应用遥测与 Azure 资源诊断是不同采集路径；表 schema 与当前配置共同决定可查内容", 1200, 590)
    p.extend([
        box(32, 148, 286, 122, "Application Insights", ["OpenTelemetry / SDK", "requests · dependencies · exceptions"], PURPLE, LAVENDER, 17),
        box(32, 328, 286, 122, "Azure resource logs", ["Diagnostic settings / DCR", "类别 · destination · transform"], TEAL, PALE, 17),
        box(388, 200, 286, 170, "Log Analytics workspace", ["tables + exact schema", "time · role · operation IDs", "table plan · retention"], NAVY, BLUE, 18),
        box(746, 200, 190, 170, "KQL query", ["scope + time range", "filter + group", "correlate"], ORANGE, SAND),
        box(1000, 200, 170, 170, "Triage", ["hotspot", "transaction", "failure cause"], GREEN, MINT, 17),
        arrow(318, 209, 378, 255, PURPLE), arrow(318, 389, 378, 315, TEAL),
        arrow(674, 285, 736, 285), arrow(936, 285, 990, 285),
        text(600, 480, "空结果先检查采集、表/列、workspace/resource scope、时间和筛选条件。", 19, RED, 700),
        text(600, 520, "有日志数据，只能证明当前可见范围中存在这些已收集记录。", 17, MUTED),
    ])
    finish(p, "telemetry-data-path.svg")


def kql_pipeline() -> None:
    p = start("KQL 是按表流动的查询管道，先缩小数据再做聚合",
              "每个 union / join 子查询都应有自己的时间约束；字段名区分大小写", 1200, 560)
    p.extend([
        box(34, 180, 180, 118, "Table", ["AppRequests", "schema is the contract"], TEAL, PALE, 17),
        box(252, 180, 190, 118, "where time", ["TimeGenerated", ">= ago(30m)"], RED, ROSE, 17),
        box(480, 180, 190, 118, "where scope", ["role / result / name", "filter early"], ORANGE, SAND, 17),
        box(708, 180, 190, 118, "project / extend", ["keep useful columns", "derive a metric"], PURPLE, LAVENDER, 17),
        box(936, 180, 230, 118, "summarize / bin", ["count + failure rate", "by time and role"], GREEN, MINT, 17),
        arrow(214, 239, 242, 239), arrow(442, 239, 470, 239), arrow(670, 239, 698, 239), arrow(898, 239, 926, 239),
        box(220, 366, 300, 92, "join / union", ["use only when needed", "align keys + time range"], NAVY, BLUE, 17),
        box(680, 366, 300, 92, "Check query details", ["time span · CPU · regions", "queue / service time"], TEAL, PALE, 17),
        arrow(370, 306, 370, 356), arrow(520, 412, 670, 412),
        text(600, 515, "Log Analytics time picker 与 KQL 时间过滤可能共同限制结果；验证最终生效范围。", 18, NAVY, 700),
    ])
    finish(p, "kql-query-pipeline.svg")


def correlation_tree() -> None:
    p = start("OperationId 找到同一分布式操作；ParentId 检查直接调用关系",
              "workspace-based Application Insights 常用 AppRequests、AppDependencies 与 AppExceptions", 1200, 570)
    p.extend([
        box(397, 116, 406, 110, "AppRequests · Checkout API", ["Id = req-17  ·  OperationId = op-7", "POST /checkout  ·  500"], RED, ROSE, 17),
        box(78, 330, 310, 112, "AppDependencies · SQL", ["Id = dep-31  ·  OperationId = op-7", "ParentId = req-17  ·  failed"], ORANGE, SAND, 16),
        box(444, 330, 310, 112, "AppExceptions · API", ["OperationId = op-7", "ParentId = req-17  ·  Timeout"], PURPLE, LAVENDER, 16),
        box(834, 330, 310, 112, "Another component", ["same OperationId", "a different role / span"], TEAL, PALE, 16),
        arrow(490, 226, 260, 320, ORANGE), arrow(600, 226, 600, 320, PURPLE), arrow(710, 226, 980, 320, TEAL),
        text(600, 494, "同一 OperationId 是关联线索；ParentId + Id 验证直接父子。不能只凭时间接近认定因果。", 18, NAVY, 700),
        text(600, 532, "采样、未插桩或过滤可能让某些 span 缺席；图中的连线不是完整性保证。", 16, MUTED),
    ])
    finish(p, "operation-correlation.svg")


def transaction_timeline() -> None:
    p = start("从总体失败率下钻到一笔请求的依赖和异常",
              "事件使用合成数据；按 OperationId 取样本，再检查 ParentId 与各 span 的具体字段", 1200, 590)
    p.extend([
        text(154, 132, "时间", 17, MUTED, 700),
        '<path d="M170,180 L1080,180" stroke="#91a7b6" stroke-width="2"/>',
        *[f'<path d="M{x},168 L{x},192" stroke="#91a7b6" stroke-width="2"/>' + text(x, 155, str(i), 16, MUTED)
          for i,x in enumerate((230, 520, 810, 1060))],
        box(66, 228, 320, 120, "Request · checkout-api", ["op-7 / req-17", "POST /checkout → 500 · 560 ms"], RED, ROSE, 17),
        box(442, 228, 320, 120, "Dependency · SQL", ["op-7 / dep-31 / parent req-17", "target payments-db → timeout"], ORANGE, SAND, 16),
        box(818, 228, 320, 120, "Exception · API", ["op-7 / parent req-17", "SqlTimeoutException"], PURPLE, LAVENDER, 17),
        arrow(386, 286, 432, 286, ORANGE), arrow(762, 286, 808, 286, PURPLE),
        text(600, 420, "视图给出一条可调查的证据链，不替代数据库端、网络端或应用日志中的根因证据。", 19, NAVY, 700),
        text(600, 472, "请求成功率异常 → 锁定 OperationId → 检查依赖成功/耗时 → 查看异常类型与栈信息。", 18, TEAL, 700),
        text(600, 528, "Application Map 看组件拓扑与热点；Transaction diagnostics 查看单次 end-to-end 细节。", 16, MUTED),
    ])
    finish(p, "transaction-timeline.svg")


def sampling_and_gaps() -> None:
    p = start("采样改变“保留了几行”和“代表了多少事件”的关系",
              "ItemCount 可加权还原代表数量的估计；采样不补回未插桩或未被采集的内容", 1200, 540)
    p.extend([
        box(52, 158, 280, 140, "原始遥测", ["4 个 checkout 请求", "4 个 request spans"], NAVY, BLUE, 18),
        box(458, 158, 280, 140, "采样后保留", ["存储 1 行", "ItemCount = 4"], ORANGE, SAND, 18),
        box(864, 158, 280, 140, "KQL 聚合", ["count() = 1 行", "sum(ItemCount) = 4"], GREEN, MINT, 18),
        arrow(332, 228, 448, 228), arrow(738, 228, 854, 228),
        '<rect x="72" y="364" width="1056" height="90" rx="16" fill="#fff0f1" stroke="#aa4052" stroke-width="2"/>',
        text(600, 400, "若依赖 span 不见了：检查插桩 / exporter / sampling / ingestion / 表与 scope / 时间过滤。", 19, RED, 700),
        text(600, 435, "“当前查询没有行”只能证明该查询没有返回行，不能证明请求或故障没发生。", 18, NAVY, 700),
        text(600, 502, "图中采样比例是用于解释 ItemCount 的教学例，不承诺特定 SDK 的每条 span 行为。", 16, MUTED),
    ])
    finish(p, "sampling-and-missing-telemetry.svg")


if __name__ == "__main__":
    data_path()
    kql_pipeline()
    correlation_tree()
    transaction_timeline()
    sampling_and_gaps()
