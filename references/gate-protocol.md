# Gate Protocol

Gate decisions are written into `GATE.md`.

## Status Values

- `PASS`: no blocking issue remains.
- `CONDITIONAL_PASS`: only partial issues remain, each has a mitigation plan, and the next stage can absorb the risk.
- `BLOCK`: at least one required artifact or one hard condition is missing.

## Gate File Template

```markdown
# Gate: Stage N - Name

**Status**: PASS | CONDITIONAL_PASS | BLOCK
**Checked At**: YYYY-MM-DD
**Checked By**: User / Agent

## Passed Items
- [x] ...

## Conditional Items
- [ ] ...
Mitigation: ...

## Blocking Items
- [ ] ...
Fix: ...

## Decision Rationale
...

## Next Action
...
```

## Implicit Gate Trigger

If the user asks to start the next stage, check the current stage gate first. If `GATE.md` is absent, run `scripts/gate_check.py` and ask the user to resolve blocking items or approve a conditional pass.
