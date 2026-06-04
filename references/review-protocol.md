# Review Protocol

Run review in this order and write each report as Markdown.

## Review 1: Format

First extract the template or venue requirements. Then check:

- Page size, margins, columns, font size, line spacing.
- Figure and table margins, caption position, numbering, cross-references.
- Equations inserted as formulas, not plain text; equations must be numbered when the style requires it.
- Reference format, DOI presence, bibliography style, and in-text citation style.
- Section heading levels and title capitalization.
- Table width and figure resolution.

Report path:

`stage/6-review/artifacts/review-1-format/report.md`

## Review 2: Logic And Experiment Completeness

Check:

- Research question, method, experiment, and conclusion form a closed loop.
- Every central claim has mapped evidence.
- Baselines are appropriate and not cherry-picked.
- Ablations and sensitivity checks cover the method's actual components.
- Statistical tests or multi-seed stability support performance claims.
- Limitations are honest and do not contradict conclusions.

Report path:

`stage/6-review/artifacts/review-2-logic/report.md`

## Review 3: Language

Run only after format and logic blockers are resolved.

Check:

- Terminology consistency.
- Paragraph flow and topic sentences.
- Tense, article usage, punctuation, and unit formatting.
- Overclaiming and vague phrases.
- Abstract and introduction alignment with final results.

Report path:

`stage/6-review/artifacts/review-3-language/report.md`

## Issue Levels

| Level | Meaning | Action |
|---|---|---|
| Critical | Data error, logic break, unsupported conclusion, ethics issue | Must fix |
| High | Major evidence, readability, or reproducibility risk | Fix before submission |
| Medium | Terminology, maintainability, or minor structure issue | Schedule fix |
| Low | Style or optional polish | Optional |
