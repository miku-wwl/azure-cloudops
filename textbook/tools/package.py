#!/usr/bin/env python3
"""打包两个最终交付物，并做一致性与敏感信息检查。

    python tools/package.py            # 生成 dist/ 下两个 ZIP
    python tools/package.py --verify   # 只校验现有 ZIP 与 dist/pdf、源稿是否一致

1) <PDF ZIP>：dist/pdf 下的 23 个 PDF（原样，不重新压缩内容）
2) <源稿 ZIP>：textbook/ 下全部可编辑源稿与实验工程。文件清单取自 git（已跟踪 + 未被 .gitignore 忽略的新文件），
   因而与仓库内容一致；再额外排除 dist/ 与下列兜底规则（构建中间产物、Terraform 缓存与锁文件、状态文件、
   字节码、*.local.* 本机文件）。文本内容统一为 LF 换行，避免 Windows 与 Linux 工作树换行差异；二进制内容原样保留。
   不在 git 仓库中运行时退回为遍历目录 + 兜底规则。

敏感信息检查：若存在 tools/sensitive.local.txt（每行一个正则，本机专用、不入库），
会扫描所有将被打包的文本文件，命中即失败退出。
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # textbook/
DIST = ROOT / "dist"
PDF_ZIP = DIST / "Azure-CloudOps-PDF.zip"
SRC_ZIP = DIST / "Azure-CloudOps-Sources.zip"

EXCLUDE_DIRS = {".terraform", "build", "work", "__pycache__", "dist", ".pytest_cache"}
EXCLUDE_NAMES = {"plan.json", "tfplan", "crash.log"}
EXCLUDE_SUFFIX = {".pyc", ".tfstate", ".tfplan", ".tfvars", ".pem", ".key"}
TEXT_SUFFIX = {".md", ".txt", ".json", ".jsonl", ".py", ".sh", ".tf", ".hcl", ".yml", ".yaml",
               ".js", ".css", ".ps1", ".cwli", ".example", ".html", ".svg"}


def included(p: Path) -> bool:
    rel = p.relative_to(ROOT)
    if any(part in EXCLUDE_DIRS for part in rel.parts[:-1]):
        return False
    if p.name in EXCLUDE_NAMES or p.suffix in EXCLUDE_SUFFIX:
        return False
    if ".local." in p.name or p.name.startswith(".env"):
        return False
    return True


def candidates() -> list[Path]:
    """git 认为应入库的文件（已跟踪 + 未被忽略的新文件）；不在 git 仓库中时退回遍历目录。"""
    try:
        out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                             cwd=ROOT, capture_output=True, check=True).stdout
        return [ROOT / n for n in out.decode("utf-8").split("\0") if n]
    except (OSError, subprocess.CalledProcessError):
        return list(ROOT.rglob("*"))


def source_files() -> list[Path]:
    return sorted({p for p in candidates() if p.is_file() and included(p)})


def deny_patterns() -> re.Pattern | None:
    f = ROOT / "tools" / "sensitive.local.txt"
    if not f.exists():
        return None
    pats = [ln.strip() for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")]
    return re.compile("|".join(pats), re.I) if pats else None


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_bytes(path: Path) -> bytes:
    """Return portable archive bytes, normalizing only known text formats to LF."""
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIX:
        return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data


def build() -> None:
    pdfs = sorted((DIST / "pdf").glob("*.pdf"))
    if len(pdfs) != 23:
        sys.exit(f"dist/pdf 中应有 23 个 PDF，实际 {len(pdfs)} 个")
    deny = deny_patterns()
    leaks = []
    files = source_files()
    if deny:
        for p in files:
            if p.suffix.lower() in TEXT_SUFFIX and deny.search(p.read_text(encoding="utf-8", errors="ignore")):
                leaks.append(str(p.relative_to(ROOT)))
    if leaks:
        sys.exit("发现敏感字符串，停止打包：\n  " + "\n  ".join(leaks))
    with zipfile.ZipFile(PDF_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in pdfs:
            z.write(p, f"Azure-CloudOps-PDF/{p.name}")
    with zipfile.ZipFile(SRC_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            arcname = "Azure-CloudOps-sources/" + p.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo.from_file(p, arcname)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, source_bytes(p))
    print(f"{PDF_ZIP.name}: {len(pdfs)} 个 PDF，{PDF_ZIP.stat().st_size / 1e6:.1f} MB")
    print(f"{SRC_ZIP.name}: {len(files)} 个文件，{SRC_ZIP.stat().st_size / 1e6:.1f} MB")
    print("敏感信息检查：" + ("通过" if deny else "跳过（没有 tools/sensitive.local.txt）"))


def verify() -> bool:
    ok = True
    with zipfile.ZipFile(PDF_ZIP) as z:
        if z.testzip():
            print("PDF ZIP 损坏"); ok = False
        inzip = {Path(n).name: sha256(z.read(n)) for n in z.namelist()}
    ondisk = {p.name: sha256(p.read_bytes()) for p in (DIST / "pdf").glob("*.pdf")}
    diff = sorted(set(inzip.items()) ^ set(ondisk.items()))
    print(f"PDF ZIP：{len(inzip)} 个文件，与 dist/pdf 逐字节{'一致' if not diff else '不一致：' + str(diff[:3])}")
    ok &= not diff
    with zipfile.ZipFile(SRC_ZIP) as z:
        if z.testzip():
            print("源稿 ZIP 损坏"); ok = False
        inzip = {n.split("/", 1)[1]: sha256(z.read(n)) for n in z.namelist()}
    ondisk = {p.relative_to(ROOT).as_posix(): sha256(source_bytes(p)) for p in source_files()}
    diff = sorted(set(inzip.items()) ^ set(ondisk.items()))
    print(f"源稿 ZIP：{len(inzip)} 个文件，与 textbook/ 源稿（文本统一 LF）逐字节{'一致' if not diff else '不一致：' + str([d[0] for d in diff[:5]])}")
    ok &= not diff
    return ok


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    if not a.verify:
        build()
    sys.exit(0 if verify() else 1)
