# Rollback Protocol

Use rollback when later work invalidates earlier assumptions.

## Common Paths

| Situation | Rollback |
|---|---|
| Results do not support the hypothesis | Stage 3 -> Stage 2 |
| Outline lacks enough evidence | Stage 4 -> Stage 3 |
| Draft story is incoherent | Stage 5 -> Stage 4 |
| Review finds unsupported claims | Stage 6 -> Stage 4 or Stage 3 |
| Review finds experiment design flaw | Stage 6 -> Stage 2 |

## Rollback Record

Write records under `stage/rollback/`.

```markdown
# Rollback: Stage X -> Stage Y

**Time**: YYYY-MM-DD
**Reason**: ...
**Problem**: ...
**Affected Artifacts**:
- ...
**Recovery Plan**:
- ...
**Estimated Cost**: ...
```

## Restrictions

- Do not silently delete later-stage work.
- If content freeze exists, write an unfreeze note before changing frozen content.
- If the same issue causes three rollbacks, stop and ask for human decision.
