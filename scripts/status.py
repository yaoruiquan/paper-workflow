#!/usr/bin/env python3
"""打印论文工作流状态。"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from common import read_key_value_file, resolve_project_dir


STAGES = [
    (1, "topic"),
    (2, "experiment-design"),
    (3, "experiment-run"),
    (4, "outline"),
    (5, "writing"),
    (6, "review"),
]


def read_env(root: Path) -> dict[str, str]:
    return read_key_value_file(root / ".paper-workflow.env")


def gate_status(stage_dir: Path) -> str:
    gate = stage_dir / "GATE.md"
    if not gate.exists():
        return "无关卡"
    text = gate.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"\*\*(?:Status|状态)\*\*\s*:\s*([A-Z_]+)", text)
    return match.group(1) if match else "未知"


def main() -> int:
    parser = argparse.ArgumentParser(description="打印论文工作流状态")
    parser.add_argument("project_dir", help="论文项目目录。相对路径会解析到 PAPER_WORKFLOW_ROOT 下。")
    args = parser.parse_args()
    root = resolve_project_dir(args.project_dir)
    env = read_env(root)
    print(f"项目: {root}")
    print(f"标题: {env.get('PAPER_TITLE', '') or '待填写'}")
    print(f"论文类型: {env.get('PAPER_PROFILE', 'generic') or 'generic'}")
    print(f"当前阶段: {env.get('CURRENT_STAGE', 'unknown')} {env.get('CURRENT_STAGE_NAME', '')}")
    print("")
    print("| 阶段 | 目录 | 关卡 |")
    print("|---:|---|---|")
    for number, slug in STAGES:
        stage_dir = root / "stage" / f"{number}-{slug}"
        exists = "存在" if stage_dir.exists() else "缺失"
        print(f"| {number} | stage/{number}-{slug} ({exists}) | {gate_status(stage_dir)} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
