#!/usr/bin/env python3
"""检查论文工作流阶段必需产物。"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


STAGE_SLUGS = {
    1: "topic",
    2: "experiment-design",
    3: "experiment-run",
    4: "outline",
    5: "writing",
    6: "review",
}

STAGE_LABELS = {
    1: "选题",
    2: "实验设计",
    3: "实验运行",
    4: "大纲",
    5: "写作",
    6: "审查",
}

REQUIRED = {
    1: [
        "artifacts/topic-proposal.md",
        "artifacts/gap-analysis.md",
        "artifacts/literature-survey.md",
        "artifacts/core-refs.bib",
        "artifacts/feasibility-check.md",
    ],
    2: [
        "artifacts/experiment-design.md",
        "artifacts/evaluation-protocol.md",
        "artifacts/baseline-results.md",
        "artifacts/project-check.md",
    ],
    3: [
        "artifacts/main-results",
        "artifacts/experiment-log.md",
        "artifacts/anomaly-report.md",
        "artifacts/statistical-tests",
    ],
    4: [
        "artifacts/outline.md",
        "artifacts/page-budget.md",
        "artifacts/storyline.md",
        "artifacts/section-experiment-map.md",
    ],
    5: [
        "drafts/v1",
        "drafts/v2",
        "checkpoints/content-freeze.md",
    ],
    6: [
        "artifacts/review-1-format/report.md",
        "artifacts/review-2-logic/report.md",
        "artifacts/review-3-language/report.md",
        "artifacts/final-check/submission-ready.md",
    ],
}


def is_present(path: Path) -> bool:
    if path.is_dir():
        return any(path.iterdir())
    if path.is_file():
        return bool(path.read_text(encoding="utf-8", errors="ignore").strip())
    return False


def check_stage(root: Path, stage: int) -> tuple[str, list[tuple[str, bool]]]:
    slug = STAGE_SLUGS[stage]
    stage_dir = root / "stage" / f"{stage}-{slug}"
    rows = [(item, is_present(stage_dir / item)) for item in REQUIRED[stage]]
    status = "PASS" if all(ok for _, ok in rows) else "BLOCK"
    return status, rows


def report_text(stage: int, status: str, rows: list[tuple[str, bool]]) -> str:
    lines = [
        f"# 关卡检查：阶段 {stage} - {STAGE_LABELS[stage]}",
        "",
        f"**状态**: {status}",
        f"**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 必需项",
        "",
    ]
    for item, ok in rows:
        mark = "x" if ok else " "
        lines.append(f"- [{mark}] {item}")
    lines.extend(["", "## 阻塞项", ""])
    missing = [item for item, ok in rows if not ok]
    if missing:
        lines.extend(f"- {item}" for item in missing)
    else:
        lines.append("- 无")
    lines.extend(["", "## 下一步动作", ""])
    lines.append("写入 `GATE.md`，记录最终 `PASS` / `CONDITIONAL_PASS` / `BLOCK` 判定。")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="检查阶段关卡")
    parser.add_argument("project_dir")
    parser.add_argument("--stage", type=int, required=True, choices=sorted(STAGE_SLUGS))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    root = Path(args.project_dir).expanduser().resolve()
    status, rows = check_stage(root, args.stage)
    text = report_text(args.stage, status, rows)
    if not args.no_write:
        out = root / "stage" / f"{args.stage}-{STAGE_SLUGS[args.stage]}" / "gate-check.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"已写入: {out}")
    print(text)
    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
