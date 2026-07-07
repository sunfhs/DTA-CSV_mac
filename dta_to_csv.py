#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd


CHUNKSIZE = 20_000
NO_UI = os.environ.get("DTA_TO_CSV_NO_UI") == "1"


def notify(message: str) -> None:
    if NO_UI:
        return
    subprocess.run(
        [
            "osascript",
            "-e",
            f'display notification "{message.replace(chr(34), chr(39))}" with title "DTA 转 CSV"',
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def alert(message: str) -> None:
    if NO_UI:
        print(message)
        return
    subprocess.run(
        [
            "osascript",
            "-e",
            f'display dialog "{message.replace(chr(34), chr(39))}" buttons {{"好"}} default button "好"',
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def progress(kind: str, index: int, total: int, text: str) -> None:
    if NO_UI:
        print(f"{kind}\t{index}\t{total}\t{text}", flush=True)


def dta_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.dta")))
        elif path.suffix.lower() == ".dta":
            files.append(path)
    return files


def output_path(source: Path, roots: list[Path]) -> Path:
    for root in roots:
        if root.is_dir():
            try:
                rel = source.relative_to(root)
            except ValueError:
                continue
            return root.parent / f"{root.name}_CSV" / rel.with_suffix(".csv")
    return source.with_suffix(".csv")


def convert_one(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()

    first = True
    for chunk in pd.read_stata(
        source,
        chunksize=CHUNKSIZE,
        convert_categoricals=False,
        preserve_dtypes=True,
    ):
        chunk.to_csv(
            target,
            mode="w" if first else "a",
            index=False,
            header=first,
            encoding="utf-8-sig",
            quoting=csv.QUOTE_MINIMAL,
        )
        first = False


def main(argv: list[str]) -> int:
    roots = [Path(arg).expanduser().resolve() for arg in argv]
    files = dta_files(roots)
    if not files:
        alert("请把 .dta 文件，或包含 .dta 文件的文件夹，拖到这个 App 图标上。")
        return 2

    notify(f"开始转换 {len(files)} 个文件")
    outputs: list[Path] = []
    errors: list[str] = []

    for index, source in enumerate(files, 1):
        target = output_path(source, roots)
        notify(f"{index}/{len(files)} {source.name}")
        progress("PROGRESS", index, len(files), source.name)
        try:
            convert_one(source, target)
            progress("DONE", index, len(files), str(target))
            outputs.append(target)
        except Exception as exc:
            errors.append(f"{source.name}: {exc}")

    if outputs:
        subprocess.run(["open", str(outputs[0].parent)], check=False)

    if errors:
        alert("部分文件转换失败：\n" + "\n".join(errors[:5]))
        return 1

    alert(f"转换完成：{len(outputs)} 个 CSV 文件。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
