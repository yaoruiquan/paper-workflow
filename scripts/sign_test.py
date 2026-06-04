#!/usr/bin/env python3
"""Run a paired two-sided sign test from CSV columns."""

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
    parser = argparse.ArgumentParser(description="Paired sign test")
    parser.add_argument("csv_path")
    parser.add_argument("--baseline-col", default="baseline")
    parser.add_argument("--method-col", default="method")
    parser.add_argument("--higher-is-better", action="store_true", default=True)
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
    print("# Paired Sign Test\n")
    print(f"- wins: {wins}")
    print(f"- losses: {losses}")
    print(f"- ties: {ties}")
    print(f"- skipped: {skipped}")
    print(f"- two_sided_p: {p_value:.6g}")
    return 0 if p_value < 0.05 else 2


if __name__ == "__main__":
    raise SystemExit(main())
