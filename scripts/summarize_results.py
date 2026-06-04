#!/usr/bin/env python3
"""Summarize numeric result files into Markdown tables."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


def rows_from_file(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else [data]
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return []


def numeric(value: Any) -> float | None:
    try:
        num = float(str(value).strip())
    except ValueError:
        return None
    return None if math.isnan(num) or math.isinf(num) else num


def summarize(path: Path) -> list[tuple[str, str, int, float]]:
    values: dict[str, list[float]] = defaultdict(list)
    for row in rows_from_file(path):
        if not isinstance(row, dict):
            continue
        for key, value in row.items():
            num = numeric(value)
            if num is not None:
                values[key].append(num)
    return [(str(path), key, len(nums), sum(nums) / len(nums)) for key, nums in values.items() if nums]


def iter_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(path for path in root.rglob("*") if path.suffix.lower() in {".csv", ".json", ".jsonl"})


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize result files")
    parser.add_argument("path")
    parser.add_argument("--output")
    args = parser.parse_args()
    root = Path(args.path).expanduser().resolve()
    lines = ["# Result Summary", "", "| File | Metric | N | Mean |", "|---|---|---:|---:|"]
    for file_path in iter_files(root):
        for source, metric, count, avg in summarize(file_path):
            lines.append(f"| {source} | {metric} | {count} | {avg:.6g} |")
    text = "\n".join(lines) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
