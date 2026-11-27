from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
RELEASES = {
    "good-v1.zip": ROOT / "good",
    "fault-v2.zip": ROOT / "bad",
}

def build(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for archive, source in RELEASES.items():
        manifest = json.loads((source / "package.json").read_text(encoding="utf-8"))
        if manifest.get("engines", {}).get("node") != "24.x":
            raise SystemExit(f"{source}: expected Node 24.x")
        with zipfile.ZipFile(out / archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for name in ("package.json", "server.js"):
                path = source / name
                if not path.is_file():
                    raise SystemExit(f"missing package file: {path}")
                z.write(path, name)
        with zipfile.ZipFile(out / archive) as z:
            if set(z.namelist()) != {"package.json", "server.js"}:
                raise SystemExit(f"unexpected entries in {archive}: {z.namelist()}")
            if bad_entry := z.testzip():
                raise SystemExit(f"failed CRC check in {archive}: {bad_entry}")
        print(f"{archive}: {manifest['name']}; root entries verified")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the two no-dependency IR-11 ZIP packages.")
    parser.add_argument("--out", type=Path, default=REPO / "work" / "azure-cloudops-ir11-packages")
    args = parser.parse_args()
    build(args.out)
