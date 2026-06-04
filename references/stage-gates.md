# Stage Gate Checklists

## Stage 1 Topic Gate

Required artifacts:

- `artifacts/topic-proposal.md`
- `artifacts/gap-analysis.md`
- `artifacts/literature-survey.md`
- `artifacts/core-refs.bib`
- `artifacts/feasibility-check.md`

Block if:

- The contribution is only a domain swap with no method or evidence novelty.
- The contribution is only hyperparameter tuning.
- The core data or compute budget is infeasible.
- The expected claim cannot be evaluated.

## Stage 2 Experiment Design Gate

Required artifacts:

- `artifacts/experiment-design.md`
- `artifacts/evaluation-protocol.md`
- `artifacts/baseline-results.md`
- `artifacts/project-check.md`

Block if:

- Baseline is not runnable.
- Metric definitions are ambiguous.
- Seed/config/commit tracking is missing.
- Estimated compute cost exceeds the available schedule.

## Stage 3 Experiment Run Gate

Required artifacts:

- `artifacts/main-results/`
- `artifacts/experiment-log.md`
- `artifacts/anomaly-report.md`
- `artifacts/statistical-tests/`

Block if:

- Main results contain unaddressed NaN/inf values.
- A key table or figure is missing.
- Multi-seed variance is unexplained.
- Results do not support the core claim and no rollback is recorded.

## Stage 4 Outline Gate

Required artifacts:

- `artifacts/outline.md`
- `artifacts/page-budget.md`
- `artifacts/storyline.md`
- `artifacts/section-experiment-map.md`

Block if:

- Any major claim lacks a mapped experiment, figure, table, or citation.
- Page budget conflicts with venue constraints.
- Experimental content is absent from the outline.

## Stage 5 Writing Gate

Required artifacts:

- `drafts/v1/`
- `drafts/v2/`
- `checkpoints/content-freeze.md`

Block if:

- Any section is empty.
- Draft contains placeholder figures or unresolved `[TODO]`.
- Terms are inconsistent across sections.
- Content freeze is requested while critical evidence is missing.

## Stage 6 Review Gate

Required artifacts:

- `artifacts/review-1-format/report.md`
- `artifacts/review-2-logic/report.md`
- `artifacts/review-3-language/report.md`
- `artifacts/final-check/submission-ready.md`

Block if:

- Format review finds template mismatch in references, equations, figures, or tables.
- Logic review finds unsupported claims.
- Experiment completeness review finds missing baselines, ablations, or statistical checks.
- Language review is being used to mask unresolved evidence problems.
