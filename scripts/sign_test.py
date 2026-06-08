#!/usr/bin/env python3
"""根据 CSV 列执行配对双侧符号检验。"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


def binom_p_two_sided(wins: int, losses: int) -> float:
    n = wins + losses
    if n == 0:
        return 1.0
    observed = min(wins, losses)
    prob = sum(math.comb(n, k) for k in range(observed + 1)) / (2 ** n)
    return min(1.0, 2 * prob)


def main() -> int:
    parser = argparse.ArgumentParser(description="配对符号检验")
    parser.add_argument("csv_path")
    parser.add_argument("--baseline-col", default="baseline")
    parser.add_argument("--method-col", default="method")
    direction = parser.add_mutually_exclusive_group()
    direction.add_argument("--higher-is-better", dest="higher_is_better", action="store_true", default=True)
    direction.add_argument("--lower-is-better", dest="higher_is_better", action="store_false")
    parser.add_argument("--output", help="将 Markdown 报告写入指定路径")
    args = parser.parse_args()

    wins = losses = ties = skipped = 0
    with Path(args.csv_path).open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                baseline = float(row[args.baseline_col])
                method = float(row[args.method_col])
            except (KeyError, ValueError):
                skipped += 1
                continue
            diff = method - baseline if args.higher_is_better else baseline - method
            if diff > 0:
                wins += 1
            elif diff < 0:
                losses += 1
            else:
                ties += 1
    p_value = binom_p_two_sided(wins, losses)
    direction_label = "higher-is-better" if args.higher_is_better else "lower-is-better"
    lines = [
        "# 配对符号检验",
        "",
        f"- 指标方向: {direction_label}",
        f"- 优于基线: {wins}",
        f"- 低于基线: {losses}",
        f"- 持平: {ties}",
        f"- 跳过: {skipped}",
        f"- 双侧 p 值: {p_value:.6g}",
        "",
    ]
    text = "\n".join(lines)
    if args.output:
        Path(args.output).expanduser().write_text(text, encoding="utf-8")
    print(text)
    return 0 if p_value < 0.05 else 2


if __name__ == "__main__":
    raise SystemExit(main())
