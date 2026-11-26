"""figlib — tiny SVG diagram toolkit for the Azure CloudOps textbook.

Every chapter keeps its diagrams as code in chapters/<id>/figures/figs.py, e.g.

    from figlib import Fig, seq
    f = Fig(760, 300)
    f.group(20, 20, 720, 260, "VPC 10.0.0.0/16", "vpc")
    f.box(60, 80, 160, 60, "Route table", ["0.0.0.0/0 → igw"], "teal")
    f.arrow((220, 110), (320, 110), "匹配最长前缀")
    f.save("route.svg")

Units are SVG px; figures are scaled to the text width (≈174 mm), so 760 px ≈ 174 mm and a
12 px label prints at roughly 8 pt. Colours follow the book palette (navy/teal/orange).
"""
from __future__ import annotations
import html
import math

FONT = "'Noto Sans SC','Microsoft YaHei',sans-serif"
MONO = "'Cascadia Mono',Consolas,monospace"
NAVY, TEAL, ORANGE, RED, GREEN, PURPLE = "#1d3b53", "#1a8a8f", "#e0954a", "#c0504d", "#2e7d55", "#6f55a8"
INK, MUTED, FAINT, LINE = "#22313d", "#5d6d7a", "#8796a3", "#9fb3c1"

BOX = {  # fill, stroke, title colour, text colour
    "teal": ("#e6f3f3", TEAL, "#12676b", INK),
    "navy": ("#e9eff5", NAVY, "#17384f", INK),
    "orange": ("#fdf1e3", ORANGE, "#9a5a1c", INK),
    "gray": ("#f2f5f7", LINE, "#41525f", MUTED),
    "white": ("#ffffff", "#b8c7d2", "#17384f", INK),
    "red": ("#fbeceb", RED, "#8e2f2c", INK),
    "green": ("#eaf5ee", GREEN, "#1f5c3d", INK),
    "purple": ("#f1edf8", PURPLE, "#4f3a86", INK),
    "solid-navy": (NAVY, NAVY, "#ffffff", "#dbe6ee"),
    "solid-teal": (TEAL, TEAL, "#ffffff", "#e3f4f4"),
    "solid-orange": (ORANGE, ORANGE, "#ffffff", "#fff4e8"),
    "solid-red": (RED, RED, "#ffffff", "#fde9e8"),
}
GROUP = {  # stroke, fill, label colour, dashed
    "cloud": ("#232f3e", "#fbfcfd", "#232f3e", False),
    "region": (TEAL, "none", "#12676b", True),
    "vpc": ("#7b5cc4", "#fbf9ff", "#5b3fa6", False),
    "az": ("#3d7fb8", "none", "#2c6596", True),
    "public": ("#4f9a3c", "#f2f8ee", "#36752a", False),
    "private": (TEAL, "#eef7f7", "#12676b", False),
    "account": ("#c0397a", "#fffafc", "#a3285f", False),
    "ou": (NAVY, "#f7f9fb", NAVY, True),
    "org": (NAVY, "#fbfcfd", NAVY, False),
    "onprem": ("#7a8691", "#f7f8f9", "#4f5a63", False),
    "plain": (LINE, "#fbfcfd", "#41525f", False),
    "dashed": (LINE, "none", "#41525f", True),
    "warn": (ORANGE, "#fffaf3", "#9a5a1c", True),
    "danger": (RED, "#fff8f8", "#8e2f2c", True),
}


def tw(s: str, size: float) -> float:
    """Approximate rendered width of a string."""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o >= 0x2E80 or ch in "，。：；！？（）、“”《》【】":
            w += 1.0
        elif ch in "il.,:;|!'`":
            w += 0.3
        elif ch in "mwMW@%":
            w += 0.85
        elif ch.isupper() or ch.isdigit():
            w += 0.62
        else:
            w += 0.53
    return w * size


def esc(s) -> str:
    return html.escape(str(s), quote=True)


class Fig:
    def __init__(self, w: int, h: int, bg: str | None = None):
        self.w, self.h = w, h
        self.items: list[str] = []
        self.markers: dict[str, str] = {}
        if bg:
            self.items.append(f'<rect x="0" y="0" width="{w}" height="{h}" fill="{bg}"/>')

    # ------------------------------------------------------------ primitives
    def raw(self, s: str):
        self.items.append(s)
        return self

    def rect(self, x, y, w, h, fill="none", stroke=LINE, sw=1.2, r=6, dash=None, opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" ry="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{o}/>')
        return self

    def circle(self, cx, cy, r, fill="none", stroke=LINE, sw=1.2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
        return self

    def line(self, x1, y1, x2, y2, color=LINE, sw=1.2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}/>')
        return self

    def path(self, d, stroke=LINE, sw=1.2, fill="none", dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}/>')
        return self

    def text(self, x, y, s, size=12, weight=400, color=INK, anchor="start", mono=False,
             italic=False, opacity=None, rotate=None):
        fam = MONO if mono else FONT
        st = ' font-style="italic"' if italic else ""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        rot = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
        self.items.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}"{st}{op}{rot}>{esc(s)}</text>')
        return self

    def lines(self, x, y, lines, size=11.5, lh=None, color=INK, anchor="middle", weight=400, mono=False):
        lh = lh or size * 1.42
        for i, s in enumerate(lines):
            m = mono or (isinstance(s, str) and s.startswith("`") and s.endswith("`"))
            s = s.strip("`") if isinstance(s, str) else s
            self.text(x, y + i * lh, s, size=size, color=color, anchor=anchor, weight=weight, mono=m)
        return self

    # ------------------------------------------------------------ composites
    def box(self, x, y, w, h, title=None, lines=(), style="teal", title_size=12.5, size=11,
            align="center", r=8, sw=1.4, dash=None, valign="center", lh=None):
        fill, stroke, tc, bc = BOX[style]
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, r=r, dash=dash)
        lh = lh or size * 1.42
        n = (1 if title else 0) + len(lines)
        block = (title_size * 1.25 if title else 0) + len(lines) * lh
        if valign == "top":
            cy = y + 10 + title_size
        else:
            cy = y + (h - block) / 2 + (title_size if title else size) * 0.92
        ax = x + w / 2 if align == "center" else x + 10
        anchor = "middle" if align == "center" else "start"
        if title:
            self.text(ax, cy, title, size=title_size, weight=700, color=tc, anchor=anchor)
            cy += title_size * 0.35 + lh
        for s in lines:
            m = isinstance(s, str) and s.startswith("`") and s.endswith("`")
            self.text(ax, cy, s.strip("`"), size=size - (0.6 if m else 0), color=bc, anchor=anchor, mono=m)
            cy += lh
        return self

    def group(self, x, y, w, h, label=None, kind="plain", size=11.5, sw=1.4, tab=True, r=6):
        stroke, fill, lc, dashed = GROUP[kind]
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, r=r, dash="6 4" if dashed else None)
        if label:
            if tab and not dashed:
                lw = tw(label, size) + 16
                self.items.append(f'<path d="M{x} {y + r} a{r} {r} 0 0 1 {r} -{r} h{lw - r} v{size + 9} h-{lw} z" fill="{stroke}"/>')
                self.text(x + 8, y + size + 3.5, label, size=size, weight=700, color="#ffffff")
            else:
                self.text(x + 9, y + size + 6, label, size=size, weight=700, color=lc)
        return self

    def _marker(self, color, kind="arrow"):
        mid = f"m{kind}{color.strip('#')}"
        if mid not in self.markers:
            if kind == "arrow":
                self.markers[mid] = (f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                                     f'<path d="M0 0.8 L9.2 5 L0 9.2 z" fill="{color}"/></marker>')
            else:  # dot
                self.markers[mid] = (f'<marker id="{mid}" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5">'
                                     f'<circle cx="5" cy="5" r="4" fill="{color}"/></marker>')
        return mid

    def arrow(self, p1, p2, label=None, color=NAVY, sw=1.6, dash=False, via=(), head="end",
              label_at=0.5, dx=0, dy=-6, label_size=10.5, label_color=None, label_bg=True, curve=0,
              label_anchor="middle", label_weight=500):
        pts = [p1, *via, p2]
        if curve and not via:
            (x1, y1), (x2, y2) = p1, p2
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            nx, ny = -(y2 - y1), (x2 - x1)
            L = math.hypot(nx, ny) or 1
            cx, cy = mx + nx / L * curve, my + ny / L * curve
            d = f"M{x1} {y1} Q{cx} {cy} {x2} {y2}"
            lx, ly = (x1 + 2 * cx + x2) / 4, (y1 + 2 * cy + y2) / 4
        else:
            d = "M" + " L".join(f"{x} {y}" for x, y in pts)
            # label on the longest segment by default
            segs = list(zip(pts, pts[1:]))
            (ax, ay), (bx, by) = max(segs, key=lambda s: math.hypot(s[1][0] - s[0][0], s[1][1] - s[0][1])) if via else segs[0]
            lx, ly = ax + (bx - ax) * label_at, ay + (by - ay) * label_at
        m = self._marker(color)
        me = f' marker-end="url(#{m})"' if head in ("end", "both") else ""
        ms = f' marker-start="url(#{m})"' if head in ("start", "both") else ""
        da = ' stroke-dasharray="5 4"' if dash else ""
        self.items.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{da}{me}{ms} stroke-linejoin="round"/>')
        if label:
            for i, part in enumerate(label.split("\n")):
                yy = ly + dy + i * (label_size * 1.3)
                if label_bg:
                    wdt = tw(part, label_size) + 8
                    bx0 = lx + dx - wdt / 2 if label_anchor == "middle" else (lx + dx - 4 if label_anchor == "start" else lx + dx - wdt + 4)
                    self.rect(bx0, yy - label_size * 0.95, wdt, label_size * 1.3, fill="#ffffff", stroke="none", r=3, opacity=0.92)
                self.text(lx + dx, yy, part, size=label_size, color=label_color or color, anchor=label_anchor, weight=label_weight)
        return self

    def badge(self, x, y, n, color=TEAL, r=9, size=10.5, fg="#ffffff"):
        self.circle(x, y, r, fill=color, stroke="none")
        self.text(x, y + size * 0.36, str(n), size=size, weight=800, color=fg, anchor="middle")
        return self

    def pill(self, x, y, s, fill="#e6f3f3", color="#12676b", size=10, weight=700, anchor="start", pad=6, mono=False):
        w = tw(s, size) + pad * 2
        x0 = x if anchor == "start" else (x - w / 2 if anchor == "middle" else x - w)
        self.rect(x0, y - size - 2, w, size + 7, fill=fill, stroke="none", r=(size + 7) / 2)
        self.text(x0 + w / 2, y + 0.5, s, size=size, weight=weight, color=color, anchor="middle", mono=mono)
        return w

    def note(self, x, y, w, h, lines, style="orange", size=10.5, title=None):
        fill, stroke, tc, bc = BOX[style]
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1, r=5, dash="4 3")
        cy = y + size + 6
        if title:
            self.text(x + 8, cy, title, size=size, weight=700, color=tc)
            cy += size * 1.45
        for s in lines:
            self.text(x + 8, cy, s, size=size, color=bc)
            cy += size * 1.45
        return self

    def legend(self, x, y, items, size=10):
        """items: list of (label, kind) where kind is 'arrow:<color>', 'dash:<color>' or a BOX style."""
        cx = x
        for label, kind in items:
            if kind.startswith(("arrow:", "dash:")):
                col = kind.split(":", 1)[1]
                self.arrow((cx, y - 3.5), (cx + 26, y - 3.5), color=col, dash=kind.startswith("dash"), sw=1.5)
                cx += 32
            else:
                fill, stroke, _, _ = BOX[kind]
                self.rect(cx, y - 10, 14, 11, fill=fill, stroke=stroke, sw=1, r=2)
                cx += 20
            self.text(cx, y, label, size=size, color=MUTED)
            cx += tw(label, size) + 18
        return self

    # simple glyphs (drawn, not AWS icon assets)
    def icon_user(self, x, y, s=16, color=NAVY):
        self.circle(x, y - s * 0.45, s * 0.28, fill=color, stroke="none")
        self.path(f"M{x - s * 0.5} {y + s * 0.42} q0 -{s * 0.62} {s * 0.5} -{s * 0.62} q{s * 0.5} 0 {s * 0.5} {s * 0.62} z", stroke="none", fill=color)
        return self

    def icon_lock(self, x, y, s=14, color=NAVY):
        self.rect(x - s / 2, y - s * 0.15, s, s * 0.7, fill=color, stroke="none", r=2)
        self.path(f"M{x - s * 0.3} {y - s * 0.15} v-{s * 0.25} a{s * 0.3} {s * 0.3} 0 0 1 {s * 0.6} 0 v{s * 0.25}", stroke=color, sw=2)
        return self

    def icon_db(self, x, y, s=18, color=NAVY):
        self.items.append(f'<ellipse cx="{x}" cy="{y - s * 0.4}" rx="{s * 0.5}" ry="{s * 0.16}" fill="none" stroke="{color}" stroke-width="1.6"/>')
        self.path(f"M{x - s * 0.5} {y - s * 0.4} v{s * 0.8} a{s * 0.5} {s * 0.16} 0 0 0 {s} 0 v-{s * 0.8}", stroke=color, sw=1.6)
        return self

    def check(self, x, y, ok=True, size=12):
        col = GREEN if ok else RED
        self.circle(x, y, size * 0.62, fill=col, stroke="none")
        if ok:
            self.path(f"M{x - size * .3} {y} l{size * .22} {size * .24} l{size * .4} -{size * .44}", stroke="#fff", sw=1.8)
        else:
            self.path(f"M{x - size * .26} {y - size * .26} l{size * .52} {size * .52} M{x + size * .26} {y - size * .26} l-{size * .52} {size * .52}", stroke="#fff", sw=1.8)
        return self

    # ------------------------------------------------------------ output
    def svg(self) -> str:
        defs = "<defs>" + "".join(self.markers.values()) + "</defs>" if self.markers else ""
        body = "\n".join(self.items)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
                f'font-family="{FONT}">\n{defs}\n{body}\n</svg>\n')

    def save(self, path: str):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.svg())
        return path


def seq(path, participants, steps, w=760, col_w=None, top=20, row=34, title=None, foot=None):
    """Sequence diagram.

    participants: list of (key, label, style)        style ∈ BOX keys
    steps: list of tuples/dicts:
        ("a", "b", "label")                     solid request
        ("b", "a", "label", "ret")              dashed return
        ("note", "a", "text") / ("note", "a:b", "text")   note spanning one or two lifelines
        ("self", "a", "label")                  self-call
        ("sep", "label")                        divider row
    """
    n = len(participants)
    margin = 18
    col_w = col_w or (w - 2 * margin) / n
    xs = {k: margin + col_w * (i + 0.5) for i, (k, _, _) in enumerate(participants)}
    head_h = 44
    y0 = top + (24 if title else 0)
    height = y0 + head_h + 16 + row * len(steps) + 24 + (22 if foot else 0)
    f = Fig(w, int(height))
    if title:
        f.text(w / 2, top + 6, title, size=13, weight=700, color=NAVY, anchor="middle")
    bw = min(col_w - 14, 150)
    for k, label, style in participants:
        parts = label.split("\n")
        f.box(xs[k] - bw / 2, y0, bw, head_h, parts[0], parts[1:], style=style, title_size=11.5, size=9.5)
    y_end = y0 + head_h + 16 + row * len(steps)
    for k, _, _ in participants:
        f.line(xs[k], y0 + head_h, xs[k], y_end, color="#b8c7d2", sw=1.2, dash="4 4")
    y = y0 + head_h + 16 + row * 0.62
    step_no = 0
    for st in steps:
        kind = st[0]
        if kind == "note":
            ks = st[1].split(":")
            x1, x2 = xs[ks[0]], xs[ks[-1]]
            lo, hi = min(x1, x2) - 60, max(x1, x2) + 60
            if len(ks) == 1:
                lo, hi = x1 - col_w * 0.45, x1 + col_w * 0.45
            f.rect(lo, y - 15, hi - lo, 24, fill="#fff8ec", stroke=ORANGE, sw=0.9, r=4)
            f.text((lo + hi) / 2, y + 1.5, st[2], size=10, color="#7a4a14", anchor="middle")
        elif kind == "sep":
            f.line(margin, y - 4, w - margin, y - 4, color="#d0dbe3", sw=1, dash="2 3")
            f.pill(w / 2, y + 1, st[1], fill="#eef4f7", color=NAVY, size=9.5, anchor="middle")
        elif kind == "self":
            x = xs[st[1]]
            step_no += 1
            f.path(f"M{x} {y - 9} h28 v14 h-26", stroke=NAVY, sw=1.4)
            f.badge(x + 44, y - 2, step_no, color=TEAL, r=6.5, size=8)
            f.text(x + 56, y + 2, st[2], size=10.5, color=INK)
        else:
            a, b, label = st[0], st[1], st[2]
            ret = len(st) > 3 and st[3] == "ret"
            err = len(st) > 3 and st[3] == "err"
            x1, x2 = xs[a], xs[b]
            col = RED if err else (MUTED if ret else NAVY)
            pad = 4 if x2 > x1 else -4
            f.arrow((x1 + pad, y), (x2 - pad, y), color=col, dash=ret, sw=1.4)
            step_no += 1
            mid = (x1 + x2) / 2
            lw = tw(label, 10.2)
            f.rect(mid - lw / 2 - 22, y - 19, lw + 26, 16, fill="#ffffff", stroke="none", r=3, opacity=0.9)
            f.text(mid + 4, y - 6, label, size=10.2, color=(RED if err else (MUTED if ret else INK)), anchor="middle")
            f.badge(mid - lw / 2 - 12, y - 10, step_no, color=(RED if err else (FAINT if ret else TEAL)), r=6.5, size=8)
        y += row
    if foot:
        f.text(w / 2, height - 10, foot, size=9.5, color=MUTED, anchor="middle")
    return f.save(path)
