#!/usr/bin/env python3
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from dta_to_csv import convert_one


with TemporaryDirectory() as tmp:
    tmpdir = Path(tmp)
    source = tmpdir / "sample.dta"
    target = tmpdir / "sample.csv"

    pd.DataFrame({"id": [1, 2], "name": ["测试", "ok"]}).to_stata(
        source,
        write_index=False,
        version=118,
    )
    convert_one(source, target)

    text = target.read_text(encoding="utf-8-sig")
    assert "id,name" in text
    assert "测试" in text

print("self-check passed")
