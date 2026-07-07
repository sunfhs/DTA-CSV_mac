#!/usr/bin/env python3
from pathlib import Path
import sys
from zipfile import ZipFile


app = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist/DTA -> CSV.app")
zip_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("dist/DTA-to-CSV-AppleSilicon.zip")

assert app.is_dir(), app
assert (app / "Contents/MacOS/DTAtoCSV").is_file()
assert (app / "Contents/Resources/DTAtoCSVCore").is_file()
assert zip_path.is_file(), zip_path

with ZipFile(zip_path) as zf:
    names = set(zf.namelist())
    assert "DTA -> CSV.app/Contents/MacOS/DTAtoCSV" in names
    assert "DTA -> CSV.app/Contents/Resources/DTAtoCSVCore" in names

print("package-check passed")
