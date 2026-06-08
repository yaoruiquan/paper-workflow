#!/usr/bin/env python3
"""初始化阶段关卡式论文项目。"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]

STAGES = [
    (1, "topic", "选题"),
    (2, "experiment-design", "实验设计"),
    (3, "experiment-run", "实验运行"),
    (4, "outline", "大纲"),
    (5, "writing", "写作"),
    (6, "review", "审查"),
]


def render_template(relative_path: str, values: dict[str, str]) -> str:
    path = SKILL_ROOT / relative_path
    text = path.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


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
            f"PAPER_PROFILE={args.profile}",
            "CURRENT_STAGE=1",
            "CURRENT_STAGE_NAME=选题",
            "AUTHOR_MODE=single",
            "EXPERIMENT_TRACKING=local",
            "",
        ]
    )


def paper_md(args: argparse.Namespace) -> str:
    return render_template(
        "assets/paper-starter/PAPER.md",
        {
            "TITLE": args.title or "未命名论文",
            "TARGET_VENUE": args.target_venue or "待填写",
            "PAGE_LIMIT": str(args.pages or "待填写"),
            "FIELD": args.field or "待填写",
            "PAPER_PROFILE": args.profile,
            "INITIALIZED_AT": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    )


def gate_check_stub(stage_num: int, name: str) -> str:
    text = render_template(
        "assets/gate-template.md",
        {
            "STAGE_NUM": str(stage_num),
            "STAGE_NAME": name,
            "DATE": datetime.now().strftime("%Y-%m-%d"),
        },
    )
    return text + f"\n在 skill 目录下运行 `python3 scripts/gate_check.py <project_dir> --stage {stage_num}`，可自动检查必需文件是否存在。\n"


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
        write_once(stage_dir / "artifacts/experiment-log.md", "# 实验日志\n\n", force=force)
        write_once(stage_dir / "artifacts/anomaly-report.md", "# 异常报告\n\n", force=force)
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
    write_once(root / "bibliography" / "references.bib", "% 在这里添加 BibTeX 参考文献。\n", force=args.force)

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
        (SKILL_ROOT / "assets" / "experiment-log-template.md").read_text(encoding="utf-8"),
        force=args.force,
    )

    for stage_num, slug, display in STAGES:
        create_stage(root, stage_num, slug, display, force=args.force)
    (root / "stage" / "rollback").mkdir(parents=True, exist_ok=True)
    return root


def main() -> int:
    parser = argparse.ArgumentParser(description="初始化论文工作流项目")
    parser.add_argument("project_dir")
    parser.add_argument("--title", default="")
    parser.add_argument("--target-venue", default="")
    parser.add_argument("--pages", type=int, default=0)
    parser.add_argument("--field", default="")
    parser.add_argument(
        "--profile",
        choices=["generic", "simulation", "ml-experiment", "engineering-design", "review"],
        default="generic",
        help="论文类型，用于选择阶段关卡要求",
    )
    parser.add_argument("--force", action="store_true", help="覆盖脚手架文件")
    args = parser.parse_args()
    root = init_project(args)
    print(f"已初始化: {root}")
    print(f"查看状态: python3 scripts/status.py {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
