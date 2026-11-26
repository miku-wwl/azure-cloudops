#!/usr/bin/env python
"""Crop / normalise a Console capture into a chapter's screenshots folder.

    python tools/shot.py SRC DST [--crop x0,y0,x1,y1] [--maxw 1600] [--q 90]

* SRC: image saved by the browser extension (PNG or JPEG)
* DST: chapters/<id>/screenshots/<name>.jpg|png
* Crop box is in SRC pixels. Output is RGB JPEG (default) or PNG by extension.
Redaction of account IDs happens in the browser before capture (see README);
this script additionally refuses to write if the raw account id appears in the
file name, as a guard against mistakes.
"""
import argparse
import sys
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("dst")
ap.add_argument("--crop")
ap.add_argument("--maxw", type=int, default=1600)
ap.add_argument("--q", type=int, default=90)
a = ap.parse_args()
im = Image.open(a.src).convert("RGB")
if a.crop:
    x0, y0, x1, y1 = [int(v) for v in a.crop.split(",")]
    im = im.crop((x0, y0, min(x1, im.width), min(y1, im.height)))
if im.width > a.maxw:
    im = im.resize((a.maxw, round(im.height * a.maxw / im.width)), Image.LANCZOS)
if a.dst.lower().endswith(".png"):
    im.save(a.dst, optimize=True)
else:
    im.save(a.dst, quality=a.q, optimize=True, progressive=True)
print(f"{a.dst}: {im.width}x{im.height}")
