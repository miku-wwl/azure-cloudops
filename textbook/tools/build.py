#!/usr/bin/env python
"""Build one chapter of the Azure CloudOps textbook.

    python tools/build.py A00-01            # figures + HTML + PDF + QA
    python tools/build.py A00-01 --no-figs  # skip figure regeneration
    python tools/build.py A00-01 --qa-only  # only re-run QA on the existing PDF

Pipeline: chapters/<id>/figures/figs.py → SVG ; chapter.md --pandoc--> HTML fragment
→ post-process (code highlighting, titled boxes, meta grids) → build/chapter.html
→ Chrome headless print → dist/pdf/<id>_<slug>.pdf → QA (contact sheets + checks).
"""
import argparse, html, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

import yaml
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name

ROOT = Path(__file__).resolve().parents[1]          # textbook/
TOOLS = ROOT / "tools"
CHAPTERS = ROOT / "chapters"
DIST = ROOT / "dist" / "pdf"
CHROME = next((p for p in [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"] if os.path.exists(p)), None)

LEXERS = {"hcl": "terraform", "tf": "terraform", "terraform": "terraform", "sh": "bash",
          "bash": "bash", "shell": "bash", "ps": "powershell", "powershell": "powershell",
          "pwsh": "powershell", "ps1": "powershell", "json": "json", "yaml": "yaml", "yml": "yaml",
          "python": "python", "py": "python", "sql": "sql", "ini": "ini", "toml": "toml",
          "diff": "diff", "xml": "xml", "js": "javascript", "javascript": "javascript",
          "go": "go", "http": "http", "dockerfile": "docker", "text": "text", "txt": "text",
          "console": "text", "output": "text", "log": "text", "rego": "text", "jq": "text"}
LANG_LABEL = {"terraform": "HCL", "bash": "Bash", "powershell": "PowerShell", "json": "JSON",
              "yaml": "YAML", "python": "Python", "sql": "SQL", "text": "", "ini": "INI",
              "toml": "TOML", "diff": "diff", "xml": "XML", "javascript": "JS", "go": "Go",
              "http": "HTTP", "docker": "Dockerfile"}


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if r.returncode != 0:
        print(r.stdout[-3000:], r.stderr[-3000:], file=sys.stderr)
        raise SystemExit(f"command failed: {cmd[0]} (exit {r.returncode})")
    return r


def read_front_matter(md_text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", md_text, re.S)
    if not m:
        raise SystemExit("chapter.md needs YAML front matter")
    return yaml.safe_load(m.group(1)), md_text[m.end():]


# ---------------------------------------------------------------- post-processing
def _hl_code(match):
    attrs, code = match.group(1), match.group(3)
    classes = re.search(r'class="([^"]*)"', attrs)
    classes = classes.group(1).split() if classes else []
    title = re.search(r'data-title="([^"]*)"', attrs)
    title = html.unescape(title.group(1)) if title else ""
    lang = next((LEXERS[c] for c in classes if c in LEXERS), "text")
    dark = any(c in ("console", "output", "log") for c in classes)
    src = html.unescape(code)
    try:
        lexer = TextLexer() if lang == "text" else get_lexer_by_name(lang)
    except Exception:
        lexer = TextLexer()
    body = highlight(src, lexer, HtmlFormatter(nowrap=True, classprefix=""))
    if dark:
        # prompt lines "$ cmd" / "PS> cmd" get the prompt colour
        body = re.sub(r"(?m)^(\$ |PS&gt; |PS [A-Z]:\\[^&]*&gt; )", r'<span class="gp">\1</span>', body)
    label = LANG_LABEL.get(lang, "") if not dark else ("终端输出" if "output" in classes else "终端")
    head = ""
    if title or label:
        head = (f'<div class="code-title"><span>{html.escape(title)}</span>'
                f'<span class="lang">{html.escape(label)}</span></div>')
    cls = "code console" if dark else "code"
    if src.count(chr(10)) <= 18:      # short blocks stay on one page
        cls += " keep"
    return f'<div class="{cls}">{head}<pre class="hl"><code>{body.rstrip()}</code></pre></div>'


def _kv_grid(div_class, inner):
    """<ul><li><strong>K</strong>：V</li>…</ul> → <div><b>K</b>V</div>…"""
    items = re.findall(r"<li>(.*?)</li>", inner, re.S)
    cells = []
    for it in items:
        it = re.sub(r"^<p>|</p>$", "", it.strip())
        m = re.match(r"<strong>(.*?)</strong>\s*[：:]?\s*(.*)", it, re.S)
        k, v = (m.group(1), m.group(2)) if m else ("", it)
        cells.append(f"<div><b>{k}</b>{v}</div>")
    return f'<div class="{div_class}">' + "".join(cells) + "</div>"


def postprocess(body):
    # title="…" on divs/pre → data-title (pandoc keeps standard attr names as-is)
    body = re.sub(r'(<(?:div|pre|section)\b[^>]*?)\stitle="', r'\1 data-title="', body)
    body = re.sub(r"<pre([^>]*)><code([^>]*)>(.*?)</code></pre>", _hl_code, body, flags=re.S)
    for cls in ("labmeta", "cover-meta"):
        body = re.sub(rf'<div class="{cls}">\s*<ul>(.*?)</ul>\s*</div>',
                      lambda m, c=cls: _kv_grid(c, m.group(1)), body, flags=re.S)
    # boxed blocks get a real title element (a ::before cannot carry break-after: avoid)
    body = re.sub(r'(<div class="(?:example|lab|fault)[^"]*" data-title="([^"]*)">)',
                  lambda m: m.group(1) + '<div class="box-title">' + m.group(2) + '</div>', body)
    # images: lazy-loading off (print), keep relative paths
    body = body.replace(' loading="lazy"', "")
    return body


TEMPLATE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>{doc_title}</title>
<meta name="author" content="Azure CloudOps 工程教材编写组">
<meta name="description" content="{subtitle}">
<style>
{css}
@page {{
  @top-left {{ content: "AZURE CLOUDOPS · 云运维工程实战"; font: 700 7pt "Noto Sans SC"; letter-spacing: .16em; color: #1d3b53;
    vertical-align: bottom; padding-bottom: 2.6mm; border-bottom: .5pt solid #d5dde3;
    background: linear-gradient(90deg,#1d3b53 0 52%,#1a8a8f 52% 100%) top/100% 1.8mm no-repeat; }}
  @top-right {{ content: "{hdr_right}"; font: 400 7pt "Noto Sans SC"; color: #5b6b78; letter-spacing: .04em;
    vertical-align: bottom; padding-bottom: 2.6mm; border-bottom: .5pt solid #d5dde3;
    background: linear-gradient(90deg,#1a8a8f 0 32%,#e0954a 32% 100%) top/100% 1.8mm no-repeat; }}
}}
</style>
<base href="../">
</head><body>
{body}
</body></html>
"""


def build_html(chap_dir, meta, md_body):
    tmp_md = chap_dir / "build" / "_body.md"
    tmp_md.write_text(md_body, encoding="utf-8")
    exts = "markdown+fenced_divs+bracketed_spans+pipe_tables+grid_tables+raw_html+implicit_figures+link_attributes+definition_lists+smart-smart"
    r = run(["pandoc", str(tmp_md), "-f", exts, "-t", "html5", "--wrap=none",
             "--syntax-highlighting=none"])
    body = postprocess(r.stdout)
    css = (TOOLS / "style.css").read_text(encoding="utf-8")
    page = TEMPLATE.format(doc_title=html.escape(f"{meta['id']} {meta['title']}"),
                           subtitle=html.escape(meta.get("subtitle", "")), css=css,
                           hdr_right=meta.get("header", f"{meta['id']}"), body=body)
    out = chap_dir / "build" / "chapter.html"
    out.write_text(page, encoding="utf-8")
    tmp_md.unlink()
    # sanity: every referenced image exists
    missing = [s for s in re.findall(r'<img[^>]+src="([^"]+)"', body)
               if not s.startswith(("http", "data:")) and not (chap_dir / s).exists()]
    if missing:
        raise SystemExit(f"missing images: {missing}")
    return out


def print_pdf(html_path, pdf_path):
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    prof = Path(tempfile.gettempdir()) / "cloudops-textbook-chrome"
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           "--generate-pdf-document-outline", f"--user-data-dir={prof}",
           "--run-all-compositor-stages-before-draw", "--virtual-time-budget=15000",
           f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()]
    run(cmd)
    if not pdf_path.exists() or pdf_path.stat().st_size < 10000:
        raise SystemExit("PDF not produced")


# ---------------------------------------------------------------- QA
def qa(pdf_path, chap_dir):
    from PIL import Image, ImageDraw, ImageFont
    import pypdf
    qdir = chap_dir / "build" / "qa"
    shutil.rmtree(qdir, ignore_errors=True)
    qdir.mkdir(parents=True)
    run(["pdftoppm", "-r", "42", "-png", str(pdf_path), str(qdir / "p")])
    pages = sorted(qdir.glob("p-*.png"), key=lambda p: int(p.stem.split("-")[1]))
    report, thumbs = [], []
    for i, p in enumerate(pages, 1):
        im = Image.open(p).convert("L")
        w, h = im.size
        top, bot = int(h * 22 / 297) + 2, int(h * (297 - 17) / 297) - 2
        left, right = int(w * 17 / 210), int(w * (210 - 17) / 210)
        body = im.crop((left, top, right, bot))
        ink = sum(1 for v in body.getdata() if v < 200) / (body.width * body.height)
        over = im.crop((right + 2, top, w, bot))
        overflow = sum(1 for v in over.getdata() if v < 150)
        # how far down the last ink row reaches (fill ratio of the page)
        rows = [y for y in range(body.height) if min(body.crop((0, y, body.width, y + 1)).getdata()) < 200]
        fill = (rows[-1] / body.height) if rows else 0
        flag = []
        if ink < 0.02: flag.append("NEAR-BLANK")
        if overflow > 3: flag.append(f"RIGHT-OVERFLOW({overflow})")
        if fill < 0.45 and i not in (1, len(pages)): flag.append(f"SHORT({fill:.0%})")
        report.append(f"p{i:02d} ink={ink:.3f} fill={fill:.0%} {' '.join(flag)}")
        thumbs.append(Image.open(p).convert("RGB"))
    # contact sheets: 4 pages per row, 2 rows per sheet
    tw, th = thumbs[0].size
    per_row, rows_per = 4, 2
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 16)
    except Exception:
        font = None
    for s in range(0, len(thumbs), per_row * rows_per):
        chunk = thumbs[s:s + per_row * rows_per]
        sheet = Image.new("RGB", (per_row * (tw + 8) + 8, ((len(chunk) - 1) // per_row + 1) * (th + 26) + 4), (120, 130, 140))
        d = ImageDraw.Draw(sheet)
        for k, t in enumerate(chunk):
            x, y = 8 + (k % per_row) * (tw + 8), 4 + (k // per_row) * (th + 26)
            sheet.paste(t, (x, y + 20))
            d.text((x, y), f"p{s + k + 1}", fill=(255, 255, 255), font=font)
        sheet.save(qdir / f"sheet-{s // (per_row * rows_per) + 1:02d}.png")
    for p in pages:
        p.unlink()
    r = pypdf.PdfReader(str(pdf_path))
    text = "\n".join((pg.extract_text() or "") for pg in r.pages)
    markers = [m for m in ("TODO", "TBD", "待补", "XXX", "NOT CAPTURED", "????") if m in text]
    summary = [f"PDF: {pdf_path.name}  pages={len(r.pages)}  size={pdf_path.stat().st_size/1024:.0f} KB",
               f"chars={len(text)}  markers={markers or 'none'}"] + report
    (qdir / "report.txt").write_text("\n".join(summary), encoding="utf-8")
    print("\n".join(summary))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chapter")
    ap.add_argument("--no-figs", action="store_true")
    ap.add_argument("--qa-only", action="store_true")
    a = ap.parse_args()
    chap_dir = CHAPTERS / a.chapter
    md = (chap_dir / "chapter.md").read_text(encoding="utf-8")
    meta, md_body = read_front_matter(md)
    pdf = DIST / f"{meta['id']}_{meta['slug']}.pdf"
    if not a.qa_only:
        (chap_dir / "build").mkdir(exist_ok=True)
        figs = chap_dir / "figures" / "figs.py"
        if figs.exists() and not a.no_figs:
            env = dict(os.environ, PYTHONPATH=str(TOOLS), PYTHONIOENCODING="utf-8")
            run([sys.executable, str(figs)], cwd=str(figs.parent), env=env)
        html_path = build_html(chap_dir, meta, md_body)
        print_pdf(html_path, pdf)
    qa(pdf, chap_dir)


if __name__ == "__main__":
    main()
