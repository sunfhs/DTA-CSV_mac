#!/usr/bin/env python3
from pathlib import Path
from subprocess import run

from PIL import Image


root = Path(__file__).parent
iconset = root / "build/DTAtoCSV.iconset"
iconset.mkdir(parents=True, exist_ok=True)
base = Image.open(root / "docs/app-icon.png").convert("RGBA")

for size in [16, 32, 128, 256, 512]:
    for scale in [1, 2]:
        px = size * scale
        name = f"icon_{size}x{size}{'@2x' if scale == 2 else ''}.png"
        base.resize((px, px), Image.Resampling.LANCZOS).save(iconset / name)

run(["iconutil", "-c", "icns", str(iconset), "-o", str(root / "build/DTAtoCSV.icns")], check=True)
