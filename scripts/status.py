#!/usr/bin/env python3
"""Print paper workflow status."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


STAGES = [
    (1, "topic"),
    (2, "experiment-design"),
    (3, "experiment-run"),
    (4, "outline"),
    (5, "writing"),
    (6, "review"),
]


def read_env(root: Path) -> dict[str, str]:
    env_path = root / ".paper-workflow.env"
    data: dict[str, str] = {}
    if not env_path.exists():
        return data
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" not in line or line.strip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def gate_status(stage_dir: Path) -> str:
    gate = stage_dir / "GATE.md"
    if not gate.exists():
        return "NO_GATE"
    text = gate.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"\*\*Status\*\*\s*:\s*([A-Z_]+)", text)
    return match.group(1) if match else "UNKNOWN"


def main() -> int:
    parser = argparse.ArgumentParser(description="Print paper workflow status")
    parser.add_argument("project_dir")
    args = parser.parse_args()
    root = Path(args.project_dir).expanduser().resolve()
    env = read_env(root)
    print(f"Project: {root}")
    print(f"Title: {env.get('PAPER_TITLE', '') or 'TBD'}")
    print(f"Current stage: {env.get('CURRENT_STAGE', 'unknown')} {env.get('CURRENT_STAGE_NAME', '')}")
    print("")
    print("| Stage | Directory | Gate |")
    print("|---:|---|---|")
    for number, slug in STAGES:
        stage_dir = root / "stage" / f"{number}-{slug}"
        exists = "exists" if stage_dir.exists() else "missing"
        print(f"| {number} | stage/{number}-{slug} ({exists}) | {gate_status(stage_dir)} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
