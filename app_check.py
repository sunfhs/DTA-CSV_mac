#!/usr/bin/env python3
from pathlib import Path
import plistlib
import sys


app = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist/DTA → CSV.app")
info = plistlib.loads((app / "Contents/Info.plist").read_bytes())

assert info["CFBundleName"] == "DTA → CSV"
assert info["CFBundleDisplayName"] == "DTA → CSV"
assert info["CFBundleExecutable"] == "DTAtoCSV"
assert (app / "Contents/Resources/DTAtoCSV.icns").stat().st_size > 0

print("app-check passed")
