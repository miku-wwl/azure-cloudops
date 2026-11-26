"""Generate editable SVG figures for AZ04-04."""

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
LINE = "#91a7b6"
WHITE = "#ffffff"


def text(x: int, y: int, value: str, size: int = 18, color: str = INK, weight: int = 400, anchor: str = "start") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="Aptos,Arial,sans-serif" font-size="{size}" '
        f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(value)}</text>'
    )


def box(x: int, y: int, w: int, h: int, title: str, lines: list[str], color: str = NAVY, fill: str = WHITE, size: int = 16) -> str:
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="17" fill="{fill}" stroke="{color}" stroke-width="2.2"/>']
    out.append(text(x + w // 2, y + 32, title, 19, color, 700, "middle"))
    for i, line in enumerate(lines):
        out.append(text(x + w // 2, y + 61 + i * 25, line, size, INK, 400, "middle"))
    return "\n".join(out)


def arrow(x1: int, y1: int, x2: int, y2: int, color: str = NAVY, dashed: bool = False) -> str:
    dash = ' stroke-dasharray="8 7"' if dashed else ""
    return (
        f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" stroke-width="3"{dash} '
        f'marker-end="url(#arrow-{color[1:]})"/>'
    )


def start(title: str, subtitle: str, width: int = 1440, height: int = 600) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<defs>',
        f'<marker id="arrow-{NAVY[1:]}" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L0,8 L9,4 z" fill="{NAVY}"/></marker>',
        f'<marker id="arrow-{TEAL[1:]}" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L0,8 L9,4 z" fill="{TEAL}"/></marker>',
        f'<marker id="arrow-{ORANGE[1:]}" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L0,8 L9,4 z" fill="{ORANGE}"/></marker>',
        f'<marker id="arrow-{GREEN[1:]}" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L0,8 L9,4 z" fill="{GREEN}"/></marker>',
        f'<marker id="arrow-{PURPLE[1:]}" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L0,8 L9,4 z" fill="{PURPLE}"/></marker>',
        '</defs>',
        f'<rect width="100%" height="100%" fill="{WHITE}"/>',
        text(34, 46, title, 27, NAVY, 700),
        text(34, 77, subtitle, 16, MUTED),
    ]


def finish(parts: list[str], filename: str) -> None:
    parts.append("</svg>")
    (OUT / filename).write_text("\n".join(parts), encoding="utf-8")


def request_gates() -> None:
    p = start("访问请求需要通过连续的独立门", "DNS 选路、网络准入、身份认证与数据授权、对象/数据库状态不能互相作证", 1440, 560)
    p.extend([
        '<rect x="28" y="110" width="1384" height="190" rx="20" fill="#f6f9fb" stroke="#d3e0e7"/>',
        '<rect x="28" y="325" width="1384" height="190" rx="20" fill="#f6f9fb" stroke="#d3e0e7"/>',
        text(52, 145, "Azure Storage / Blob", 20, TEAL, 700),
        text(52, 360, "Azure SQL Database", 20, PURPLE, 700),
        box(58, 169, 280, 98, "1 · DNS / endpoint", ["normal FQDN → private or public IP", "Blob / DFS subresource"], TEAL, PALE, 15),
        box(400, 169, 280, 98, "2 · Network path", ["private route or public firewall", "source, NSG, NVA, HTTPS"], ORANGE, SAND, 15),
        box(742, 169, 280, 98, "3 · Auth + data grant", ["Entra + Blob data role", "or approved SAS / key mode"], PURPLE, LAVENDER, 15),
        box(1084, 169, 280, 98, "4 · Object state", ["name, version, deleted state", "and operation permission"], GREEN, MINT, 15),
        box(58, 384, 280, 98, "1 · DNS / endpoint", ["logical-server FQDN", "private or public endpoint"], TEAL, PALE, 15),
        box(400, 384, 280, 98, "2 · Network path", ["firewall / PE / TCP policy", "1433 and possible redirect"], ORANGE, SAND, 15),
        box(742, 384, 280, 98, "3 · Auth + SQL grant", ["Entra or SQL authentication", "database principal + permission"], PURPLE, LAVENDER, 15),
        box(1084, 384, 280, 98, "4 · Database state", ["database, schema, data", "or verified restore target"], GREEN, MINT, 15),
    ])
    for y in (218, 433):
        p.extend([arrow(338, y, 390, y), arrow(680, y, 732, y, ORANGE), arrow(1022, y, 1074, y, PURPLE)])
    p.append(text(720, 540, "A valid token cannot repair DNS; a private route cannot grant database permission.", 16, RED, 700, "middle"))
    finish(p, "request-gates.svg")


def storage_path() -> None:
    p = start("Storage Private Endpoint 改变目标 IP，不改应用 FQDN", "DNS 视图决定客户端走私有链路还是公共端点；Storage firewall 管的是公共端点", 1440, 560)
    p.extend([
        box(36, 190, 250, 116, "Workload", ["https://acct.blob.core.windows.net", "使用标准 service FQDN"], NAVY, BLUE, 15),
        box(340, 162, 326, 160, "DNS resolution", ["CNAME → privatelink 子域", "private DNS A record", "返回 endpoint private IP"], TEAL, PALE, 16),
        box(742, 134, 300, 120, "Private Endpoint", ["blob subresource NIC", "VNet 内部私有 IP"], GREEN, MINT, 16),
        box(1098, 134, 300, 120, "Blob service", ["Private Link data path", "Storage firewall 不控制 PE 流量"], GREEN, MINT, 16),
        arrow(286, 248, 330, 248), arrow(666, 235, 732, 205, TEAL), arrow(1042, 194, 1088, 194, GREEN),
        box(742, 345, 300, 104, "Public endpoint", ["只在设计允许时使用", "selected networks / IP rules"], ORANGE, SAND, 15),
        box(1098, 345, 300, 104, "Storage firewall", ["default Deny + 明确 allow", "public network access Disabled 时拒绝"], ORANGE, SAND, 15),
        arrow(666, 275, 732, 385, ORANGE, True), arrow(1042, 397, 1088, 397, ORANGE),
        text(340, 400, "DNS 若仍返回 public IP", 16, RED, 700),
        text(340, 430, "private-only workload 会走错端点", 15, RED),
        text(720, 500, "Blob 与 DFS 是不同 subresource；ADLS 操作可能需要两者。Service Endpoint 仍连接 public endpoint。", 16, NAVY, 700, "middle"),
    ])
    finish(p, "storage-private-path.svg")


def storage_auth() -> None:
    p = start("Storage 的管理权限与 Blob 数据权限分属不同授权面", "网络准入先决定请求能否到达；访问模式随后决定谁能读取或修改对象", 1440, 560)
    p.extend([
        box(42, 200, 260, 112, "网络可达", ["PE / public firewall", "TLS + storage endpoint"], ORANGE, SAND, 15),
        box(388, 122, 370, 112, "Microsoft Entra + OAuth", ["token principal", "Storage Blob Data Reader / Contributor"], PURPLE, LAVENDER, 15),
        box(388, 263, 370, 95, "SAS", ["resource + permission + expiry", "delegated authorization"], TEAL, PALE, 15),
        box(388, 384, 370, 95, "Shared Key", ["account key authorization", "subject to account policy"], ORANGE, SAND, 15),
        box(888, 220, 340, 142, "Blob data plane", ["read / write / delete", "container and blob scope", "object/version state"], GREEN, MINT, 16),
        box(42, 398, 260, 94, "ARM management plane", ["Owner / Contributor", "manage account resource"], NAVY, BLUE, 15),
        arrow(302, 250, 378, 178, ORANGE), arrow(758, 178, 878, 250, PURPLE),
        arrow(758, 310, 878, 285, TEAL), arrow(758, 431, 878, 330, ORANGE),
        arrow(302, 440, 382, 440, NAVY, True),
        text(444, 516, "Management role alone ≠ Entra data read; listKeys permission may enable key access if Shared Key is allowed.", 16, RED, 700),
        text(1190, 440, "SAS / key do not bypass network rules", 15, MUTED, 700, "middle"),
    ])
    finish(p, "storage-auth-boundary.svg")


def recovery_map() -> None:
    p = start("恢复机制必须匹配被删资源、时间窗口与备份位置", "保护状态、恢复点和目标资源都要在操作前核实", 1440, 600)
    p.extend([
        '<rect x="34" y="114" width="672" height="428" rx="18" fill="#f5f9fb" stroke="#cbd9e2"/>',
        '<rect x="734" y="114" width="672" height="428" rx="18" fill="#f8f5fc" stroke="#d8ccec"/>',
        text(64, 153, "Azure Storage / Blob", 21, TEAL, 700),
        text(764, 153, "Azure SQL Database", 21, PURPLE, 700),
        box(62, 180, 290, 96, "Blob overwrite/delete", ["versions / soft delete", "PITR: block blobs + 3 prerequisites"], TEAL, PALE, 14),
        box(390, 180, 286, 96, "Container delete", ["container soft delete", "Blob PITR 不还原 container"], ORANGE, SAND, 14),
        box(62, 300, 290, 96, "Hierarchical namespace", ["versioning unsupported", "不能套用 Blob PITR 前提"], RED, ROSE, 14),
        box(390, 300, 286, 96, "Account deletion", ["account-level recovery plan", "与 blob 级 PITR 不同"], NAVY, BLUE, 14),
        box(62, 420, 614, 84, "核实 scope + retention + 时间点 + 当前数据影响", ["启用某项保护，不等于所需恢复点仍然可用"], GREEN, MINT, 15),
        box(762, 180, 290, 96, "Recent logical error", ["PITR within actual window", "restore creates a new database"], PURPLE, LAVENDER, 14),
        box(1090, 180, 286, 96, "Regional outage", ["geo-restore from replicated backup", "requires GRS / GZRS backup"], ORANGE, SAND, 14),
        box(762, 300, 290, 96, "Historical full backup", ["Long-term retention (LTR)", "up to 10 years when configured"], TEAL, PALE, 14),
        box(1090, 300, 286, 96, "Recovery validation", ["data + identity + network", "then approved application cutover"], GREEN, MINT, 14),
        arrow(1052, 228, 1082, 228, PURPLE), arrow(1052, 348, 1082, 348, TEAL),
        text(1064, 438, "PITR / geo / LTR restore a new target; they are not failover cutover by themselves.", 14, RED, 700, "middle"),
        text(720, 575, "A backup policy is configuration evidence; a restore drill is recovery evidence.", 18, NAVY, 700, "middle"),
    ])
    finish(p, "recovery-scope-map.svg")


def sql_flow() -> None:
    p = start("Azure SQL 的连接与恢复是两条不同流程", "先证明目标 database 可达且可授权，再验证 restore target 和应用切换", 1440, 600)
    p.extend([
        text(50, 138, "连接诊断", 20, PURPLE, 700),
        box(52, 162, 240, 94, "Server FQDN", ["normal hostname", "private DNS or public DNS"], TEAL, PALE, 14),
        box(348, 162, 240, 94, "Network", ["PE / firewall / TCP 1433", "Redirect may use more ports"], ORANGE, SAND, 14),
        box(644, 162, 240, 94, "TLS + authentication", ["validate server name", "Entra token or SQL login"], PURPLE, LAVENDER, 14),
        box(940, 162, 240, 94, "Database authorization", ["principal / user exists", "database grants"], NAVY, BLUE, 14),
        box(1234, 162, 158, 94, "Query", ["data result"], GREEN, MINT, 14),
        arrow(292, 210, 338, 210, TEAL), arrow(588, 210, 634, 210, ORANGE), arrow(884, 210, 930, 210, PURPLE), arrow(1180, 210, 1224, 210, NAVY),
        '<line x1="50" y1="302" x2="1390" y2="302" stroke="#d5dfe5" stroke-width="2"/>',
        text(50, 350, "恢复与切换", 20, GREEN, 700),
        box(52, 374, 270, 100, "Verified backup", ["PITR / geo / LTR", "actual point + permissions"], NAVY, BLUE, 14),
        box(400, 374, 270, 100, "Restore to new DB", ["target name must be free", "source remains separate"], PURPLE, LAVENDER, 14),
        box(748, 374, 270, 100, "Validate target", ["row / business invariants", "DNS, identity, TLS, grants"], TEAL, PALE, 14),
        box(1096, 374, 292, 100, "Controlled cutover", ["approved route change", "measured RTO / RPO"], GREEN, MINT, 14),
        arrow(322, 424, 390, 424, NAVY), arrow(670, 424, 738, 424, PURPLE), arrow(1018, 424, 1086, 424, TEAL),
        text(720, 530, "DNS success, login success, or restore completion each proves only one boundary.", 17, RED, 700, "middle"),
    ])
    finish(p, "sql-connect-restore-flow.svg")


if __name__ == "__main__":
    request_gates()
    storage_path()
    storage_auth()
    recovery_map()
    sql_flow()
    print("Generated 5 editable SVG figures for AZ04-04")
