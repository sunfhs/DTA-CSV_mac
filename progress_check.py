#!/usr/bin/env python3
from pathlib import Path
import os
from subprocess import run
from tempfile import TemporaryDirectory

import pandas as pd


with TemporaryDirectory() as tmp:
    tmpdir = Path(tmp)
    source = tmpdir / "sample.dta"
    pd.DataFrame({"id": [1], "name": ["ok"]}).to_stata(
        source,
        write_index=False,
        version=118,
    )

    env = os.environ.copy()
    env["DTA_TO_CSV_NO_UI"] = "1"

    result = run(
        ["python3", "dta_to_csv.py", str(source)],
        cwd=Path(__file__).parent,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert "PROGRESS\t1\t1\tsample.dta" in result.stdout
    assert "DONE\t1\t1\t" in result.stdout
    assert source.with_suffix(".csv").is_file()

print("progress-check passed")
