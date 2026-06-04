#!/usr/bin/env python3
"""Check result files for missing values, NaN/inf, and outliers."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


def numeric(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def load_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            return [data]
    return []


def quantile(values: list[float], q: float) -> float:
    if not values:
        return math.nan
    sorted_values = sorted(values)
    pos = (len(sorted_values) - 1) * q
    low = math.floor(pos)
    high = math.ceil(pos)
    if low == high:
        return sorted_values[int(pos)]
    return sorted_values[low] * (high - pos) + sorted_values[high] * (pos - low)


def analyze_file(path: Path) -> dict[str, Any]:
    rows = load_rows(path)
    missing = 0
    invalid = 0
    columns: dict[str, list[float]] = {}
    for row in rows:
        for key, value in row.items():
            if value is None or str(value).strip() == "":
                missing += 1
                continue
            num = numeric(value)
            if num is None:
                continue
            if math.isnan(num) or math.isinf(num):
                invalid += 1
                continue
            columns.setdefault(key, []).append(num)

    outliers: dict[str, int] = {}
    for key, values in columns.items():
        if len(values) < 4:
            continue
        q1 = quantile(values, 0.25)
        q3 = quantile(values, 0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        count = sum(1 for value in values if value < lower or value > upper)
        if count:
            outliers[key] = count
    return {"path": str(path), "rows": len(rows), "missing": missing, "invalid": invalid, "outliers": outliers}


def iter_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    suffixes = {".csv", ".json", ".jsonl"}
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in suffixes)


def markdown(results: list[dict[str, Any]]) -> str:
    lines = ["# Experiment Data Check", "", "| File | Rows | Missing | NaN/Inf | Outliers |", "|---|---:|---:|---:|---|"]
    for item in results:
        outliers = ", ".join(f"{key}:{value}" for key, value in item["outliers"].items()) or "-"
        lines.append(f"| {item['path']} | {item['rows']} | {item['missing']} | {item['invalid']} | {outliers} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check CSV/JSON result files")
    parser.add_argument("path")
    parser.add_argument("--output")
    args = parser.parse_args()
    results = [analyze_file(path) for path in iter_files(Path(args.path).expanduser().resolve())]
    text = markdown(results)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text)
    return 0 if all(item["missing"] == 0 and item["invalid"] == 0 for item in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
