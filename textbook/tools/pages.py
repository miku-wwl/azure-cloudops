#!/usr/bin/env python
"""Render PDF pages two-up at reading resolution for page-by-page review.
   python tools/pages.py <pdf> <outdir> [dpi] [first] [last]"""
import subprocess, sys, glob, os
from PIL import Image
pdf, out = sys.argv[1], sys.argv[2]
dpi = sys.argv[3] if len(sys.argv) > 3 else "66"
os.makedirs(out, exist_ok=True)
for f in glob.glob(os.path.join(out, "*.png")): os.remove(f)
args = ["pdftoppm", "-r", dpi, "-png"]
if len(sys.argv) > 5: args += ["-f", sys.argv[4], "-l", sys.argv[5]]
subprocess.run(args + [pdf, os.path.join(out, "pg")], check=True)
pages = sorted(glob.glob(os.path.join(out, "pg-*.png")), key=lambda p: int(p.rsplit("-", 1)[1][:-4]))
for i in range(0, len(pages), 2):
    ims = [Image.open(p).convert("RGB") for p in pages[i:i + 2]]
    w = sum(im.width for im in ims) + 12 * (len(ims) - 1)
    sheet = Image.new("RGB", (w, ims[0].height), (110, 120, 130))
    x = 0
    for im in ims:
        sheet.paste(im, (x, 0)); x += im.width + 12
    n1 = int(pages[i].rsplit("-", 1)[1][:-4])
    sheet.save(os.path.join(out, f"pair-{n1:02d}.png"))
for p in pages: os.remove(p)
print(sorted(os.listdir(out)))
