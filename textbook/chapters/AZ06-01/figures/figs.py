"""Generate original, editable SVG figures for AZ06-01."""

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
           t(x + w // 2, y + 34, title, 21, stroke, 700)]
    for i, line in enumerate(lines):
        out.append(t(x + w // 2, y + 66 + i * 25, line, size))
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


def backup_vs_replication() -> None:
    p = start("Backup 保存可选择的历史恢复点；复制支持把工作负载带到恢复区域",
              "两条路径解决不同问题，不能互相取代", 1200, 590)
    p.extend([
        box(42, 128, 230, 92, "Protected workload", ["VM / database / files"], PURPLE, LAVENDER),
        box(336, 96, 310, 146, "Azure Backup", ["policy: schedule + retention", "snapshot / vault recovery points", "LRS · ZRS · GRS / supported CRR"], TEAL, PALE, 16),
        box(336, 320, 310, 146, "Site Recovery", ["replicate disk changes", "recovery point history", "recovery plan + failover"], ORANGE, SAND, 17),
        box(734, 96, 420, 146, "Restore chosen data", ["new VM / disks / files", "verify data + app", "isolate target when testing"], GREEN, MINT, 17),
        box(734, 320, 420, 146, "Recover service in DR region", ["select point + network", "sequence app dependencies", "reprotect after production failover"], NAVY, BLUE, 16),
        arrow(272, 172, 326, 172, TEAL), arrow(272, 182, 326, 392, ORANGE),
        arrow(646, 170, 724, 170, TEAL), arrow(646, 392, 724, 392, ORANGE),
        t(600, 527, "复制会同步错误写入；备份点不会自动编排多层应用启动。", 19, RED, 700),
        t(600, 560, "图示为能力边界；实际支持依赖 datasource、region、vault 和策略。", 16, MUTED),
    ])
    finish(p, "backup-vs-replication.svg")


def consistency_levels() -> None:
    p = start("快照一致性描述恢复起点，不是业务验收结果",
              "发生写入时刻、应用协调能力和恢复后的检查共同决定可用性", 1200, 560)
    p.extend([
        box(66, 152, 300, 126, "Application-consistent", ["VSS writer / Linux scripts", "flush or quiesce app state"], GREEN, MINT, 17),
        box(450, 152, 300, 126, "File-system-consistent", ["coherent file system", "application may need fix-up"], ORANGE, SAND, 16),
        box(834, 152, 300, 126, "Crash-consistent", ["disk writes only", "memory / pending I/O may be lost"], RED, ROSE, 17),
        arrow(366, 216, 440, 216, TEAL), arrow(750, 216, 824, 216, TEAL),
        box(202, 354, 300, 92, "Restore and boot", ["job success ≠ app success"], NAVY, BLUE, 17),
        box(698, 354, 300, 92, "Application checks", ["logs · DB integrity · transactions"], PURPLE, LAVENDER, 17),
        arrow(502, 400, 688, 400, PURPLE),
        t(600, 510, "缺少更强的一致性时，使用原生恢复机制和业务不变量验证数据。", 19, NAVY, 700),
    ])
    finish(p, "consistency-levels.svg")


def restore_paths() -> None:
    p = start("从 recovery point 选择恢复位置，再定义校验关卡",
              "原位恢复会替换源磁盘；演练和调查通常需要替代目标", 1200, 560)
    p.extend([
        box(42, 190, 220, 124, "Choose recovery point", ["timestamp + consistency", "snapshot tier / vault tier"], PURPLE, LAVENDER, 17),
        box(348, 118, 250, 112, "OLR", ["replace source OS + data disks", "approved production action"], RED, ROSE, 16),
        box(348, 274, 250, 112, "ALR / restore disks", ["new target / custom VM", "isolate for recovery test"], TEAL, PALE, 16),
        box(348, 430, 250, 92, "Item-level restore", ["selected files / folders"], ORANGE, SAND),
        box(710, 188, 430, 138, "Verify before service", ["data count / hash / DB checks", "identity · DNS · dependency", "business write/read probe"], GREEN, MINT, 17),
        arrow(262, 248, 338, 174, RED), arrow(262, 252, 338, 330, TEAL), arrow(262, 254, 338, 474, ORANGE),
        arrow(598, 174, 700, 216, RED), arrow(598, 330, 700, 252, TEAL), arrow(598, 474, 700, 300, ORANGE),
        t(925, 398, "选择的目标决定是否覆盖生产写入、身份或网络。", 18, NAVY, 700),
        t(925, 437, "记录时间、作业结果、校验输出和清理残留。", 17, MUTED),
    ])
    finish(p, "restore-paths.svg")


def site_recovery_flow() -> None:
    p = start("Site Recovery 编排 VM 故障转移和应用依赖",
              "测试与正式 failover 有不同目标；正式切换后还要建立反向保护", 1200, 590)
    p.extend([
        box(34, 190, 220, 130, "Primary workload", ["disk write changes", "replication agent / flow"], PURPLE, LAVENDER, 16),
        box(338, 110, 286, 124, "Latest processed", ["already applied point", "low start-up delay"], TEAL, PALE, 17),
        box(338, 296, 286, 124, "Latest", ["process data already sent", "lower RPO · may wait longer"], ORANGE, SAND, 17),
        box(716, 110, 198, 124, "Recovery plan", ["DB → API → web", "dependency order"], NAVY, BLUE, 17),
        box(716, 296, 198, 124, "Isolated test", ["validate and cleanup", "no production claim"], GREEN, MINT, 16),
        box(982, 204, 184, 140, "Production failover", ["verify service", "reprotect", "plan failback"], RED, ROSE, 16),
        arrow(254, 230, 328, 170, TEAL), arrow(254, 270, 328, 356, ORANGE),
        arrow(624, 170, 706, 170, NAVY), arrow(624, 356, 706, 356, GREEN),
        arrow(914, 172, 972, 238, RED), arrow(914, 356, 972, 302, GREEN, True),
        t(600, 495, "Site Recovery 只能处理已经送达服务的数据；latest 不是零 RPO。", 18, RED, 700),
        t(600, 535, "正式 failover 后，目标 VM 起初处于未保护状态；reprotect 是后续步骤。", 17, MUTED),
    ])
    finish(p, "site-recovery-flow.svg")


def rpo_rto_timeline() -> None:
    p = start("RPO 和 RTO 的终点要按业务定义测量",
              "RPO 看故障时刻和数据恢复点；RTO 到数据与应用验证通过", 1200, 590)
    p.extend([
        t(600, 142, "示意时间线 · 单位：分钟", 17, MUTED, 700),
        '<path d="M124,226 L1080,226" stroke="#91a7b6" stroke-width="3"/>',
        *[f'<path d="M{x},215 L{x},238" stroke="#91a7b6" stroke-width="2"/>' + t(x, 204, label, 16, MUTED)
          for x, label in ((180, "09:52"), (500, "10:00"), (686, "10:05"), (1000, "10:43"))],
        box(58, 280, 220, 96, "Recovery point", ["09:52"], TEAL, PALE),
        box(390, 280, 220, 96, "Failure detected", ["10:00"], RED, ROSE),
        box(628, 280, 220, 96, "Restore starts", ["10:05"], ORANGE, SAND),
        box(890, 280, 260, 96, "Service verified", ["10:43 · checks pass"], GREEN, MINT),
        arrow(278, 328, 380, 328, RED),
        t(330, 309, "RPO = 8m", 17, RED, 700),
        arrow(500, 397, 1000, 397, GREEN),
        t(750, 423, "RTO = 43m (业务中断 → 服务验证)", 17, GREEN, 700),
        box(202, 445, 796, 80, "Integrity + application gates", ["checksum / record invariants → DB recovery → identity & dependencies → user-path probe"], NAVY, BLUE, 17),
        t(600, 557, "VM running 不是 RTO 终点；以恢复并验证的业务服务为终点。", 18, NAVY, 700),
    ])
    finish(p, "rpo-rto-timeline.svg")


if __name__ == "__main__":
    backup_vs_replication()
    consistency_levels()
    restore_paths()
    site_recovery_flow()
    rpo_rto_timeline()
