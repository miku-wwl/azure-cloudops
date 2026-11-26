"""Generate editable SVG mechanisms for AZ06-02."""

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


def t(x: int, y: int, value: str, size: int = 19, color: str = INK,
      weight: int = 400, anchor: str = "middle") -> str:
    return (f'<text x="{x}" y="{y}" font-family="Aptos,Arial,sans-serif" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="{anchor}">{escape(value)}</text>')


def lines(x: int, y: int, values: list[str], size: int = 16,
          color: str = INK, anchor: str = "middle", step: int = 24) -> str:
    return "\n".join(t(x, y + i * step, value, size, color, 400, anchor)
                     for i, value in enumerate(values))


def box(x: int, y: int, w: int, h: int, title: str, body: list[str],
        stroke: str = NAVY, fill: str = WHITE, body_size: int = 16) -> str:
    return "\n".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>',
        t(x + w // 2, y + 31, title, 20, stroke, 700),
        lines(x + w // 2, y + 59, body, body_size, INK, "middle", 23),
    ])


def start(title: str, subtitle: str, width: int = 1200,
          height: int = 570) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        t(34, 40, title, 27, NAVY, 700, "start"),
        t(34, 72, subtitle, 17, MUTED, 400, "start"),
    ]


def arrow(x1: int, y1: int, x2: int, y2: int, color: str = NAVY,
          dashed: bool = False) -> str:
    dash = ' stroke-dasharray="8 7"' if dashed else ""
    return (f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" '
            f'stroke-width="3"{dash} marker-end="url(#arrow)"/>')


def finish(parts: list[str], filename: str) -> None:
    parts.insert(1, '<defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="5" orient="auto"><path d="M0,0 L0,10 L11,5 z" fill="#17324d"/></marker></defs>')
    parts.append("</svg>")
    (OUT / filename).write_text("\n".join(parts), encoding="utf-8")


def incident_command() -> None:
    p = start("清晰的角色让事故从检测走到可控恢复",
              "先降低用户影响；RCA 与复盘接收被保留的证据", 1200, 560)
    steps = [
        (34, "01  检测与分级", ["业务影响", "严重度 / run ID"], TEAL, PALE),
        (267, "02  遏制", ["限制范围", "冻结高风险变更"], ORANGE, SAND),
        (500, "03  调查", ["记录假设", "保留时间线证据"], PURPLE, LAVENDER),
        (733, "04  恢复", ["最小修复", "同一业务探针"], GREEN, MINT),
        (966, "05  关闭 / RCA", ["稳定 + 数据校验", "行动项有负责人"], NAVY, BLUE),
    ]
    for x, title, body, color, fill in steps:
        p.append(box(x, 122, 200, 112, title, body, color, fill, 15))
    for x in (234, 467, 700, 933):
        p.append(arrow(x, 177, x + 27, 177))
    p.extend([
        t(70, 307, "Incident Response Manager", 19, NAVY, 700, "start"),
        t(360, 307, "技术负责人", 19, TEAL, 700, "start"),
        t(590, 307, "服务 / 数据所有者", 19, ORANGE, 700, "start"),
        t(870, 307, "沟通负责人", 19, PURPLE, 700, "start"),
        lines(70, 340, ["定严重度、节奏、升级", "控制关闭闸门"], 16, INK, "start", 26),
        lines(360, 340, ["维护证据和竞争假设", "声明未知与置信边界"], 16, INK, "start", 26),
        lines(590, 340, ["批准身份、路由、数据变更", "确认回滚和完整性"], 16, INK, "start", 26),
        lines(870, 340, ["固定更新频率", "告知用户影响和恢复状态"], 16, INK, "start", 26),
        '<rect x="44" y="420" width="1110" height="83" rx="16" fill="#f5f7fa" stroke="#b7c5d0" stroke-width="2"/>',
        t(599, 452, "关闭前的三个闸门", 20, NAVY, 700),
        t(599, 482, "业务探针恢复  +  数据/安全断言通过  +  影响范围稳定", 18, GREEN, 700),
    ])
    finish(p, "incident-command.svg")


def evidence_timeline() -> None:
    p = start("按事件发生时间排序，但保留记录到达时间",
              "时间均为 UTC；Log Analytics 到达次序不等于业务因果次序", 1200, 610)
    p.append('<line x1="70" y1="170" x2="1130" y2="170" stroke="#9aabba" stroke-width="3"/>')
    top = [
        (80, "09:57", "基线探针", GREEN), (225, "10:00", "发布 v2", ORANGE),
        (370, "10:03", "首个 403", RED), (515, "10:04", "告警", PURPLE),
        (660, "10:06", "冻结发布", ORANGE), (805, "10:09", "证据区分", TEAL),
        (950, "10:13", "限域修复", GREEN), (1090, "10:21", "稳定验证", NAVY),
    ]
    for x, stamp, label, color in top:
        p.append(f'<circle cx="{x}" cy="170" r="9" fill="{color}"/>')
        p.append(f'<line x1="{x}" y1="179" x2="{x}" y2="205" stroke="{color}" stroke-width="2"/>')
        p.append(t(x, 230, stamp, 18, color, 700))
        p.append(t(x, 258, label, 15, INK, 600))
    p.extend([
        '<rect x="94" y="310" width="470" height="78" rx="14" fill="#edf5f7" stroke="#087f8c" stroke-width="2"/>',
        t(329, 339, "事件时间：dependency 403 · 10:03:00", 18, TEAL, 700),
        t(329, 367, "记录时间：TimeGenerated 保留业务事件时间", 16, INK),
        '<rect x="638" y="310" width="468" height="78" rx="14" fill="#fff3e5" stroke="#c96a18" stroke-width="2"/>',
        t(872, 339, "到达 / 可查询时间：示例为 10:04:10", 18, ORANGE, 700),
        t(872, 367, "ingestion_time() 可晚于事件；存两列，不倒置顺序", 16, INK),
        arrow(564, 349, 628, 349, ORANGE),
        '<rect x="94" y="432" width="1012" height="90" rx="14" fill="#f5f7fa" stroke="#b7c5d0" stroke-width="2"/>',
        t(600, 465, "诊断时间线至少记录", 19, NAVY, 700),
        t(600, 497, "event time · collection/ingestion time · UTC offset · source/schema · resource scope · operation ID · sampling · query window", 15, INK),
    ])
    finish(p, "evidence-timeline.svg")


def hypothesis_matrix() -> None:
    p = start("每个假设都必须预测一条能区分它的观测",
              "“支持 / 削弱 / 未知”比强行打分更诚实", 1200, 650)
    cols = [(48, 200, "假设"), (250, 355, "预测"), (610, 410, "合成请求证据"), (1025, 130, "状态")]
    for x, w, title in cols:
        p.append(f'<rect x="{x}" y="110" width="{w}" height="42" fill="#eaf1f8" stroke="#b7c5d0"/>')
        p.append(t(x + w // 2, 138, title, 16, NAVY, 700))
    rows = [
        ("身份授权", ["token 正确；数据权限缺失"], ["Storage 403；principal=v2", "rates 无 reader 角色"], "支持", TEAL, PALE),
        ("Private DNS", ["FQDN 返回错误目标"], ["期望私有 IP；TCP 已建立"], "削弱", ORANGE, SAND),
        ("NSG / 路由", ["路径连接被拒绝/超时"], ["服务返回授权 403"], "削弱", ORANGE, SAND),
        ("数据库", ["SQL 依赖或账本约束失败"], ["SQL 成功；账本 hash/行数稳定"], "削弱", GREEN, MINT),
        ("平台事件", ["匹配 service/region/time"], ["快照无匹配事件"], "未知", PURPLE, LAVENDER),
    ]
    y = 152
    h = 91
    for title, prediction, observation, state, color, fill in rows:
        p.append(f'<rect x="48" y="{y}" width="200" height="{h}" fill="{fill}" stroke="#c8d3dc"/>')
        p.append(t(148, y + 47, title, 18, color, 700))
        p.append(f'<rect x="250" y="{y}" width="355" height="{h}" fill="#ffffff" stroke="#c8d3dc"/>')
        p.append(lines(267, y + 34, prediction, 15, INK, "start", 23))
        p.append(f'<rect x="610" y="{y}" width="410" height="{h}" fill="#ffffff" stroke="#c8d3dc"/>')
        p.append(lines(627, y + 34, observation, 15, INK, "start", 23))
        p.append(f'<rect x="1025" y="{y}" width="130" height="{h}" fill="{fill}" stroke="#c8d3dc"/>')
        p.append(t(1090, y + 49, state, 18, color, 700))
        y += h
    p.append(t(600, 630, "没有诊断设置 / trace 断链 / 数据未到达 → 未知，不是反证。", 17, RED, 700))
    finish(p, "hypothesis-matrix.svg")


def causal_chain() -> None:
    p = start("根因链拆分触发、失效机制、业务影响和控制缺口",
              "相关时间相邻；具体依赖拒绝与受控修复才检验因果机制", 1200, 610)
    cards = [
        (34, "发布 v2", ["10:00 UTC", "身份绑定改变"], ORANGE, SAND),
        (266, "新主体", ["payments-mi-v2", "无 rates reader"], PURPLE, LAVENDER),
        (498, "依赖失败", ["读取 rates 得 403", "主体 ID 已关联"], RED, ROSE),
        (730, "API 失败", ["支付请求 503", "队列开始增长"], ORANGE, SAND),
        (962, "业务影响", ["部分转账被拒", "账本未损坏"], NAVY, BLUE),
    ]
    for x, title, body, color, fill in cards:
        p.append(box(x, 142, 204, 120, title, body, color, fill, 16))
    for x in (238, 470, 702, 934):
        p.append(arrow(x, 202, x + 24, 202))
    p.extend([
        '<rect x="130" y="337" width="940" height="91" rx="16" fill="#eaf6ef" stroke="#23764d" stroke-width="2.5"/>',
        t(600, 372, "受控反事实：只给 payments-mi-v2 在 rates 容器读权限", 20, GREEN, 700),
        t(600, 406, "相同请求变成功；settlement-archive 仍拒绝 → 支持角色缺口为机制", 17, INK),
        '<rect x="130" y="462" width="940" height="84" rx="16" fill="#f5f7fa" stroke="#9aabba" stroke-width="2"/>',
        t(600, 494, "系统促成条件：发布门只测进程存活，没有用目标身份读取业务配置", 18, NAVY, 700),
        t(600, 524, "预防控制：candidate-identity dependency probe + 权限差异审查 + 可验证回滚", 16, INK),
    ])
    finish(p, "causal-chain.svg")


def bounded_repair() -> None:
    p = start("修复范围越小，越容易验证副作用和回滚边界",
              "精确主体 · 精确数据范围 · 精确角色 · 原业务探针", 1200, 600)
    p.extend([
        box(46, 126, 245, 124, "1 · 保留基线", ["冻结后续发布", "保存版本 / 主体 / 证据"], TEAL, PALE, 16),
        box(330, 126, 245, 124, "2 · 单项修复", ["payments-mi-v2", "Blob Data Reader"], GREEN, MINT, 16),
        box(614, 126, 245, 124, "3 · 锁定 scope", ["rates container", "不扩大到账户/订阅"], PURPLE, LAVENDER, 16),
        box(898, 126, 245, 124, "4 · 原路径验证", ["同 transfer + 幂等键", "API 与 storage 成功"], NAVY, BLUE, 16),
        arrow(291, 187, 320, 187), arrow(575, 187, 604, 187), arrow(859, 187, 888, 187),
        '<rect x="47" y="310" width="515" height="161" rx="16" fill="#eaf6ef" stroke="#23764d" stroke-width="2.5"/>',
        t(304, 346, "必须通过", 20, GREEN, 700),
        lines(304, 378, ["账本约束 + checksum 稳定", "重复键只记一笔", "settlement-archive 仍拒绝", "5 分钟稳定 + 队列回落"], 16, INK, "middle", 24),
        '<rect x="638" y="310" width="515" height="161" rx="16" fill="#fff0f1" stroke="#aa4052" stroke-width="2.5"/>',
        t(895, 346, "必须拒绝", 20, RED, 700),
        lines(895, 378, ["Owner / Contributor 兜底提权", "关闭 NSG / 防火墙排障", "只看 /health/live 就关单", "改了多项还无法定位效果"], 16, INK, "middle", 24),
        t(600, 535, "任一数据、安全或同探针断言失败 → 保持未恢复，按预案回滚/继续遏制。", 17, RED, 700),
    ])
    finish(p, "bounded-repair.svg")


def main() -> None:
    incident_command()
    evidence_timeline()
    hypothesis_matrix()
    causal_chain()
    bounded_repair()
    print("Generated five original AZ06-02 SVG figures.")


if __name__ == "__main__":
    main()
