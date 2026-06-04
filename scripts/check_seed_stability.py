#!/usr/bin/env python3
"""Check multi-seed metric stability from a CSV file."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    return math.sqrt(sum((value - avg) ** 2 for value in values) / (len(values) - 1))


def main() -> int:
    parser = argparse.ArgumentParser(description="Check seed stability")
    parser.add_argument("csv_path")
    parser.add_argument("--group-col", default="experiment")
    parser.add_argument("--metric-col", default="metric")
    parser.add_argument("--seed-col", default="seed")
    parser.add_argument("--value-col", default="value")
    parser.add_argument("--cv-threshold", type=float, default=0.05)
    args = parser.parse_args()

    groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    with Path(args.csv_path).open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                value = float(row[args.value_col])
            except (KeyError, ValueError):
                continue
            key = (row.get(args.group_col, ""), row.get(args.metric_col, ""))
            groups[key].append(value)

    lines = ["# Seed Stability", "", "| Experiment | Metric | N | Mean | Std | CV | Status |", "|---|---|---:|---:|---:|---:|---|"]
    has_unstable = False
    for (experiment, metric), values in sorted(groups.items()):
        avg = mean(values)
        std = stdev(values)
        cv = 0.0 if avg == 0 else abs(std / avg)
        status = "UNSTABLE" if len(values) >= 2 and cv > args.cv_threshold else "OK"
        has_unstable = has_unstable or status == "UNSTABLE"
        lines.append(f"| {experiment} | {metric} | {len(values)} | {avg:.6g} | {std:.6g} | {cv:.4f} | {status} |")
    print("\n".join(lines) + "\n")
    return 2 if has_unstable else 0


if __name__ == "__main__":
    raise SystemExit(main())
