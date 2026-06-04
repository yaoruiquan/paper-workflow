# Experiment Project Rules

Use a maintainable local project. Every experiment must be traceable.

## Required Directories

```text
experiment/
├── configs/
├── data/
├── src/
├── scripts/
├── results/
│   ├── raw/
│   └── processed/
├── figures/
└── logs/
```

## Required Run Metadata

For each experiment run, record:

- Experiment ID
- Date/time
- Git commit or code snapshot note
- Dataset version
- Config file path
- Random seed
- Hardware/runtime notes
- Raw output path
- Processed result path
- Figure/table path if generated
- Known anomalies

## Data Checks

After each result batch:

- Run `scripts/check_stat.py` on result files.
- Run `scripts/check_seed_stability.py` when multiple seeds exist.
- Compare baseline reproduction to reported values when available.
- Record anomalies in `stage/3-experiment-run/artifacts/anomaly-report.md`.

## Figure Checks

Figures should be publication-ready before Stage 4:

- Use readable fonts and consistent sizes.
- Export vector formats when possible (`.pdf`, `.svg`) and high-resolution raster otherwise.
- Keep axis labels, legends, and captions consistent with the paper terminology.
- Do not use screenshots for quantitative figures.
