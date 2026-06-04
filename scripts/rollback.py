#!/usr/bin/env python3
"""Create a rollback record for a paper workflow project."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


STAGE_NAMES = {
    1: "topic",
    2: "experiment-design",
    3: "experiment-run",
    4: "outline",
    5: "writing",
    6: "review",
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
    parser = argparse.ArgumentParser(description="Write a rollback record")
    parser.add_argument("project_dir")
    parser.add_argument("--from-stage", type=int, required=True, choices=range(1, 7))
    parser.add_argument("--to-stage", type=int, required=True, choices=range(1, 7))
    parser.add_argument("--reason", required=True)
    parser.add_argument("--problem", default="")
    parser.add_argument("--recovery-plan", default="")
    parser.add_argument("--estimated-cost", default="")
    args = parser.parse_args()
    if args.to_stage >= args.from_stage:
        raise SystemExit("--to-stage must be earlier than --from-stage")
    root = Path(args.project_dir).expanduser().resolve()
    rollback_dir = root / "stage" / "rollback"
    rollback_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = rollback_dir / f"rollback-{args.from_stage}-to-{args.to_stage}-{stamp}.md"
    text = f"""# Rollback: Stage {args.from_stage} -> Stage {args.to_stage}

**Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Reason**: {args.reason}
**Problem**: {args.problem or 'TBD'}

## Affected Artifacts

- TBD

## Recovery Plan

{args.recovery_plan or 'TBD'}

## Estimated Cost

{args.estimated_cost or 'TBD'}
"""
    out.write_text(text, encoding="utf-8")
    update_env(root, args.to_stage)
    print(f"wrote: {out}")
    print(f"current stage: {args.to_stage} {STAGE_NAMES[args.to_stage]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
