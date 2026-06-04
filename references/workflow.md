# Paper Workflow

Use a Stage + Gate + Rollback model. The goal is to prevent paper writing from drifting away from evidence.

## Stage Overview

| Stage | Name | Main Output | Gate Purpose |
|---|---|---|---|
| 1 | Topic | Topic proposal, gap analysis, literature survey | Avoid weak or infeasible topics |
| 2 | Experiment design | Experiment design, protocol, baseline plan | Ensure experiments can answer the research question |
| 3 | Experiment run | Raw/processed results, figures, anomaly notes | Ensure results are complete and reasonable |
| 4 | Outline | Page budget, storyline, section-experiment map | Ensure writing has evidence before drafting |
| 5 | Writing | Versioned drafts and content-freeze note | Ensure drafts converge instead of drifting |
| 6 | Review | Format, logic, and language review reports | Ensure submission readiness |

## Operating Rules

- Write every non-trivial result into a file under the current stage.
- Never move forward on chat-only conclusions.
- Before entering a new stage, check the previous stage gate.
- If later work reveals missing evidence, use rollback instead of patching prose around the gap.
- Keep experiments reproducible with config, seed, commit, metric, and run logs.

## Recommended Project Structure

```text
project/
├── .paper-workflow.env
├── PAPER.md
├── bibliography/
│   └── references.bib
├── experiment/
│   ├── configs/
│   ├── data/
│   ├── src/
│   ├── scripts/
│   ├── results/
│   │   ├── raw/
│   │   └── processed/
│   ├── figures/
│   └── logs/
└── stage/
    ├── 1-topic/
    ├── 2-experiment-design/
    ├── 3-experiment-run/
    ├── 4-outline/
    ├── 5-writing/
    └── 6-review/
```

## Stage Handoff

Every stage should end with:

- `gate-check.md`: checklist generated or updated before decision.
- `GATE.md`: final decision: `PASS`, `CONDITIONAL_PASS`, or `BLOCK`.
- A clear next action if the gate is not `PASS`.
