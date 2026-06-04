#!/usr/bin/env python3
"""Initialize a stage-gated paper project."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


STAGES = [
    (1, "topic", "Topic"),
    (2, "experiment-design", "Experiment Design"),
    (3, "experiment-run", "Experiment Run"),
    (4, "outline", "Outline"),
    (5, "writing", "Writing"),
    (6, "review", "Review"),
]


def write_once(path: Path, text: str, force: bool = False) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def env_text(args: argparse.Namespace) -> str:
    return "\n".join(
        [
            f"PAPER_TITLE={args.title or ''}",
            f"TARGET_VENUE={args.target_venue or ''}",
            f"PAGE_LIMIT={args.pages or ''}",
            f"FIELD={args.field or ''}",
            "CURRENT_STAGE=1",
            "CURRENT_STAGE_NAME=topic",
            "AUTHOR_MODE=single",
            "EXPERIMENT_TRACKING=local",
            "",
        ]
    )


def paper_md(args: argparse.Namespace) -> str:
    return f"""# {args.title or 'Untitled Paper'}

**Target Venue**: {args.target_venue or 'TBD'}
**Page Limit**: {args.pages or 'TBD'}
**Field**: {args.field or 'TBD'}
**Initialized At**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Research Question

TBD

## Contribution

TBD

## Current Stage

Stage 1 - Topic

## Notes

Use `stage/` artifacts and `GATE.md` files as the source of truth.
"""


def gate_check_stub(stage_num: int, name: str) -> str:
    return f"""# Gate Check: Stage {stage_num} - {name}

**Status**: BLOCK
**Updated At**: {datetime.now().strftime('%Y-%m-%d')}

## Required Items

- [ ] Fill this stage's required artifacts.

## Notes

Run `python3 scripts/gate_check.py <project_dir> --stage {stage_num}` from the skill directory for an automated file-presence check.
"""


def create_stage(root: Path, stage_num: int, slug: str, display: str, force: bool = False) -> None:
    stage_dir = root / "stage" / f"{stage_num}-{slug}"
    (stage_dir / "artifacts").mkdir(parents=True, exist_ok=True)
    write_once(stage_dir / "gate-check.md", gate_check_stub(stage_num, display), force=force)
    if stage_num == 3:
        for child in [
            "artifacts/main-results/raw",
            "artifacts/main-results/processed",
            "artifacts/main-results/figures",
            "artifacts/ablation",
            "artifacts/sensitivity",
            "artifacts/statistical-tests",
        ]:
            (stage_dir / child).mkdir(parents=True, exist_ok=True)
        write_once(stage_dir / "artifacts/experiment-log.md", "# Experiment Log\n\n", force=force)
        write_once(stage_dir / "artifacts/anomaly-report.md", "# Anomaly Report\n\n", force=force)
    if stage_num == 5:
        for version in ["v1", "v2", "v3"]:
            (stage_dir / "drafts" / version).mkdir(parents=True, exist_ok=True)
        (stage_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
    if stage_num == 6:
        for child in [
            "artifacts/review-1-format",
            "artifacts/review-2-logic",
            "artifacts/review-3-language",
            "artifacts/final-check",
        ]:
            (stage_dir / child).mkdir(parents=True, exist_ok=True)


def init_project(args: argparse.Namespace) -> Path:
    root = Path(args.project_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    write_once(root / ".paper-workflow.env", env_text(args), force=args.force)
    write_once(root / "PAPER.md", paper_md(args), force=args.force)
    write_once(root / "bibliography" / "references.bib", "% Add BibTeX references here.\n", force=args.force)

    for child in [
        "experiment/configs",
        "experiment/data",
        "experiment/src",
        "experiment/scripts",
        "experiment/results/raw",
        "experiment/results/processed",
        "experiment/figures",
        "experiment/logs",
    ]:
        (root / child).mkdir(parents=True, exist_ok=True)

    write_once(
        root / "experiment" / "logs" / "experiment-log.md",
        "# Experiment Log\n\n| Run ID | Date | Commit | Config | Dataset | Seed | Output | Status | Notes |\n|---|---|---|---|---|---:|---|---|---|\n",
        force=args.force,
    )

    for stage_num, slug, display in STAGES:
        create_stage(root, stage_num, slug, display, force=args.force)
    (root / "stage" / "rollback").mkdir(parents=True, exist_ok=True)
    return root


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a paper workflow project")
    parser.add_argument("project_dir")
    parser.add_argument("--title", default="")
    parser.add_argument("--target-venue", default="")
    parser.add_argument("--pages", type=int, default=0)
    parser.add_argument("--field", default="")
    parser.add_argument("--force", action="store_true", help="overwrite scaffold files")
    args = parser.parse_args()
    root = init_project(args)
    print(f"initialized: {root}")
    print(f"status: python3 scripts/status.py {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
