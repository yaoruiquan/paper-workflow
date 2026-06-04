#!/usr/bin/env python3
"""根据 CSV 文件检查多随机种子指标稳定性。"""

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
    parser = argparse.ArgumentParser(description="检查随机种子稳定性")
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

    lines = ["# 随机种子稳定性", "", "| 实验 | 指标 | 样本数 | 均值 | 标准差 | 变异系数 | 状态 |", "|---|---|---:|---:|---:|---:|---|"]
    has_unstable = False
    for (experiment, metric), values in sorted(groups.items()):
        avg = mean(values)
        std = stdev(values)
        cv = 0.0 if avg == 0 else abs(std / avg)
        status = "不稳定" if len(values) >= 2 and cv > args.cv_threshold else "正常"
        has_unstable = has_unstable or status == "不稳定"
        lines.append(f"| {experiment} | {metric} | {len(values)} | {avg:.6g} | {std:.6g} | {cv:.4f} | {status} |")
    print("\n".join(lines) + "\n")
    return 2 if has_unstable else 0


if __name__ == "__main__":
    raise SystemExit(main())
