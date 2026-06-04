#!/usr/bin/env python3
"""为论文工作流项目创建回退记录。"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


STAGE_NAMES = {
    1: "选题",
    2: "实验设计",
    3: "实验运行",
    4: "大纲",
    5: "写作",
    6: "审查",
}


def update_env(root: Path, target_stage: int) -> None:
    env_path = root / ".paper-workflow.env"
    lines = []
    seen_stage = False
    seen_name = False
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()
    updated = []
    for line in lines:
        if line.startswith("CURRENT_STAGE="):
            updated.append(f"CURRENT_STAGE={target_stage}")
            seen_stage = True
        elif line.startswith("CURRENT_STAGE_NAME="):
            updated.append(f"CURRENT_STAGE_NAME={STAGE_NAMES[target_stage]}")
            seen_name = True
        else:
            updated.append(line)
    if not seen_stage:
        updated.append(f"CURRENT_STAGE={target_stage}")
    if not seen_name:
        updated.append(f"CURRENT_STAGE_NAME={STAGE_NAMES[target_stage]}")
    env_path.write_text("\n".join(updated).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="写入回退记录")
    parser.add_argument("project_dir")
    parser.add_argument("--from-stage", type=int, required=True, choices=range(1, 7))
    parser.add_argument("--to-stage", type=int, required=True, choices=range(1, 7))
    parser.add_argument("--reason", required=True)
    parser.add_argument("--problem", default="")
    parser.add_argument("--recovery-plan", default="")
    parser.add_argument("--estimated-cost", default="")
    args = parser.parse_args()
    if args.to_stage >= args.from_stage:
        raise SystemExit("--to-stage 必须早于 --from-stage")
    root = Path(args.project_dir).expanduser().resolve()
    rollback_dir = root / "stage" / "rollback"
    rollback_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = rollback_dir / f"rollback-{args.from_stage}-to-{args.to_stage}-{stamp}.md"
    text = f"""# 回退：阶段 {args.from_stage} -> 阶段 {args.to_stage}

**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**原因**: {args.reason}
**问题**: {args.problem or '待填写'}

## 受影响产物

- 待填写

## 恢复计划

{args.recovery_plan or '待填写'}

## 预计成本

{args.estimated_cost or '待填写'}
"""
    out.write_text(text, encoding="utf-8")
    update_env(root, args.to_stage)
    print(f"已写入: {out}")
    print(f"当前阶段: {args.to_stage} {STAGE_NAMES[args.to_stage]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
