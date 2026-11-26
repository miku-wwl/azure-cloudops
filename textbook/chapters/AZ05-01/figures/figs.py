"""Generate original, editable SVG figures for AZ05-01."""

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
LINE = "#91a7b6"
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
        out.append(text(x + w // 2, y + 68 + i * 27, line, size))
    return "\n".join(out)


def start(title: str, subtitle: str, width: int = 1200, height: int = 520) -> list[str]:
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="#ffffff"/>',
            text(34, 42, title, 27, NAVY, 700, "start"),
            text(34, 74, subtitle, 17, MUTED, 400, "start")]


def arrow(x1: int, y1: int, x2: int, y2: int, color: str = NAVY, dashed: bool = False) -> str:
    dash = ' stroke-dasharray="9 7"' if dashed else ""
    return (f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" '
            f'stroke-width="3"{dash} marker-end="url(#arrow)"/>')


def finish(parts: list[str], filename: str) -> None:
    parts.insert(1, f'<defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="5" orient="auto"><path d="M0,0 L0,10 L11,5 z" fill="{NAVY}"/></marker></defs>')
    parts.append("</svg>")
    (OUT / filename).write_text("\n".join(parts), encoding="utf-8")


def metric_pipeline() -> None:
    p = start("指标告警是一条从时间序列到独立告警条件的处理链",
              "先确定数据系列和聚合，再看阈值如何评估；通知位于检测之后")
    p.extend([
        box(30, 170, 210, 132, "Resource metric", ["metric name + namespace", "time, value, dimensions"], TEAL, PALE),
        box(278, 170, 210, 132, "Series selection", ["resource scope", "split or roll up dimensions"], PURPLE, LAVENDER),
        box(526, 170, 210, 132, "Rule evaluation", ["aggregation + lookback", "operator + threshold"], ORANGE, SAND),
        box(774, 170, 180, 132, "Alert condition", ["Fired / Resolved", "stateful or stateless"], RED, ROSE),
        box(990, 170, 180, 132, "Response", ["action group", "processing rules"], GREEN, MINT),
        arrow(240, 236, 268, 236), arrow(488, 236, 516, 236), arrow(736, 236, 764, 236), arrow(954, 236, 980, 236),
        text(870, 365, "检测条件", 18, RED, 700),
        text(1080, 365, "通知与抑制", 18, GREEN, 700),
        arrow(870, 330, 870, 383, RED, True), arrow(1080, 330, 1080, 383, GREEN, True),
        text(600, 455, "告警规则回答“条件是否成立”；通知处理回答“成立后如何响应”。", 21, NAVY, 700),
    ])
    finish(p, "metric-alert-pipeline.svg")


def aggregate_and_split() -> None:
    p = start("聚合方式与维度拆分会改变被比较的值",
              "合成例：server-a=40，server-b=96，阈值为 90；指标单位与服务定义仍须核对", 1200, 560)
    p.extend([
        box(40, 150, 220, 126, "两个维度系列", ["server-a  →  40", "server-b  →  96"], TEAL, PALE, 20),
        box(360, 128, 330, 140, "跨系列 Average", ["(40 + 96) / 2 = 68", "68 > 90 ?   否"], ORANGE, SAND, 20),
        box(360, 328, 330, 140, "跨系列 Maximum", ["max(40, 96) = 96", "96 > 90 ?   是"], PURPLE, LAVENDER, 20),
        box(812, 150, 330, 126, "不拆分维度", ["一个汇总条件", "平均值可能掩盖局部热点"], RED, ROSE, 19),
        box(812, 328, 330, 140, "按 server 拆分", ["server-a: 40 → 不触发", "server-b: 96 → 单独触发"], GREEN, MINT, 19),
        arrow(260, 211, 350, 198), arrow(260, 220, 350, 398),
        arrow(690, 198, 802, 198, ORANGE), arrow(690, 398, 802, 398, GREEN),
        text(600, 525, "Count 是样本/记录数，不是数值相加；Average、Sum、Min、Max 必须符合指标语义。", 18, NAVY, 700),
    ])
    finish(p, "aggregation-dimensions.svg")


def evaluation_window() -> None:
    p = start("检查频率决定何时评估；回看窗口决定每次取多长的数据",
              "示例采用每 1 分钟检查、回看 3 分钟；Azure 指标采样和服务延迟不由这张示意图决定", 1200, 570)
    p.extend([
        text(54, 138, "分钟", 17, MUTED, 700, "start"),
        '<path d="M100,180 L1100,180" stroke="#91a7b6" stroke-width="2"/>',
        *[f'<path d="M{x},168 L{x},192" stroke="#91a7b6" stroke-width="2"/>' + text(x, 157, str(i), 17, MUTED, 400)
          for i, x in enumerate((180, 360, 540, 720, 900, 1080), 0)],
        *[f'<circle cx="{x}" cy="180" r="9" fill="{TEAL}"/>' for x in (180, 360, 540, 720, 900, 1080)],
        '<rect x="181" y="224" width="539" height="58" rx="12" fill="#eaf6ef" stroke="#23764d" stroke-width="2"/>',
        text(450, 260, "评估时刻 t=3：窗口 (0, 3]", 20, GREEN, 700),
        '<rect x="361" y="308" width="539" height="58" rx="12" fill="#edf5f7" stroke="#087f8c" stroke-width="2"/>',
        text(630, 344, "评估时刻 t=4：窗口 (1, 4]", 20, TEAL, 700),
        '<rect x="541" y="392" width="539" height="58" rx="12" fill="#fff3e5" stroke="#c96a18" stroke-width="2"/>',
        text(810, 428, "评估时刻 t=5：窗口 (2, 5]", 20, ORANGE, 700),
        text(600, 502, "窗口彼此重叠；同一数据点可能出现在多次评估里。检查频率 ≠ 回看时长。", 20, NAVY, 700),
        text(600, 540, "本地练习用规则桶演示边界，不模拟 Azure 指标预聚合、延迟或缺失数据策略。", 16, MUTED),
    ])
    finish(p, "evaluation-window.svg")


def condition_and_notification() -> None:
    p = start("监控条件、通知动作与人工响应属于不同状态",
              "状态型规则默认会抑制持续 Fired 期间的重复告警；处理规则可影响动作处理，不改写检测条件", 1200, 580)
    p.extend([
        text(52, 136, "检测条件（示意）", 18, RED, 700, "start"),
        box(50, 164, 220, 104, "阈值违规", ["condition = Fired"], RED, ROSE),
        box(340, 164, 230, 104, "状态型规则", ["首次违规时发出", "满足恢复条件后 Resolved"], PURPLE, LAVENDER, 17),
        box(640, 164, 220, 104, "动作处理", ["action group", "processing rule"], GREEN, MINT),
        box(930, 164, 220, 104, "人工响应", ["New → Acknowledged", "→ Closed"], NAVY, BLUE, 17),
        arrow(270, 216, 330, 216), arrow(570, 216, 630, 216), arrow(860, 216, 920, 216),
        text(602, 342, "两个并行状态", 18, NAVY, 700),
        '<path d="M90,390 L1100,390" stroke="#aa4052" stroke-width="4"/>',
        *[f'<circle cx="{x}" cy="390" r="11" fill="{c}"/>' for x,c in ((180,RED),(360,RED),(540,ORANGE),(720,GREEN),(900,RED))],
        *[text(x, 427, lab, 16, col, 700) for x,lab,col in ((180,"Fired",RED),(360,"持续违规",RED),(540,"正常 1",ORANGE),(720,"正常 3：Resolved",GREEN),(900,"再次违规",RED))],
        '<path d="M90,482 L1100,482" stroke="#17324d" stroke-width="3" stroke-dasharray="10 7"/>',
        *[f'<circle cx="{x}" cy="482" r="9" fill="{NAVY}"/>' for x in (180, 520, 800, 1050)],
        *[text(x, 519, lab, 15, NAVY, 700) for x,lab in ((180,"New"),(520,"Acknowledged"),(800,"Closed"),(1050,"人员工作流"))],
        text(600, 560, "确认/关闭是使用者响应；不等于监控条件已恢复。具体恢复时间与配置应按规则核实。", 15, MUTED),
    ])
    finish(p, "alert-and-response-state.svg")


def dynamic_history() -> None:
    p = start("动态阈值需要足够历史，历史就绪不等于告警已验证",
              "官方文档列出最低样本历史与更长季节性历史要求；服务行为应结合具体指标和规则检查", 1200, 510)
    p.extend([
        '<path d="M115,250 L1080,250" stroke="#91a7b6" stroke-width="3"/>',
        '<rect x="115" y="186" width="255" height="125" rx="16" fill="#fff0f1" stroke="#aa4052" stroke-width="2"/>',
        text(242, 220, "不足 3 天", 21, RED, 700), text(242, 255, "或不足 30 个样本", 17), text(242, 287, "历史不足", 17, RED, 700),
        '<rect x="398" y="186" width="352" height="125" rx="16" fill="#fff3e5" stroke="#c96a18" stroke-width="2"/>',
        text(574, 220, "≥ 3 天且 ≥ 30 个样本", 20, ORANGE, 700), text(574, 255, "可建立基本阈值基线", 17), text(574, 287, "周周期模式仍可能不足", 17, ORANGE, 700),
        '<rect x="778" y="186" width="310" height="125" rx="16" fill="#eaf6ef" stroke="#23764d" stroke-width="2"/>',
        text(933, 220, "约 3 周历史", 21, GREEN, 700), text(933, 255, "支持学习周季节性", 17), text(933, 287, "仍需观察与调参", 17, GREEN, 700),
        *[f'<circle cx="{x}" cy="250" r="8" fill="{c}"/>' for x,c in ((115,RED),(370,ORANGE),(750,GREEN),(1080,GREEN))],
        text(600, 382, "历史门槛用于规划就绪度；本地模型只分类天数与样本数，不训练 Azure 的动态阈值模型。", 19, NAVY, 700),
        text(600, 430, "检查告警规则的维度、观测数据、无数据行为、历史范围、误报和漏报，再决定是否启用。", 17, MUTED),
    ])
    finish(p, "dynamic-threshold-history.svg")


if __name__ == "__main__":
    metric_pipeline()
    aggregate_and_split()
    evaluation_window()
    condition_and_notification()
    dynamic_history()
