# paper-workflow

Local maintenance note only. Operational instructions live in `SKILL.md`; detailed rules live in `references/`; reusable templates live in `assets/`; deterministic checks live in `scripts/`.

Codex path:

```text
/Users/yao/.codex/skills/paper-workflow
```

This path is currently symlinked to:

```text
/Users/yao/.claude/skills/paper-workflow
```

Run a smoke check after edits:

```bash
python3 -m py_compile scripts/*.py
python3 scripts/init_paper.py /private/tmp/paper-workflow-smoke --title "Smoke" --target-venue "Test" --pages 6 --profile simulation
python3 scripts/status.py /private/tmp/paper-workflow-smoke
```
