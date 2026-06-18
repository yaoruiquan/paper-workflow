"""Shared helpers for paper-workflow scripts."""

from __future__ import annotations

import os
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read_key_value_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        data[key.strip()] = value.strip().strip("\"'")
    return data


def skill_env() -> dict[str, str]:
    return read_key_value_file(SKILL_ROOT / ".env")


def workflow_root() -> Path | None:
    configured = os.environ.get("PAPER_WORKFLOW_ROOT") or skill_env().get("PAPER_WORKFLOW_ROOT")
    if not configured:
        return None
    return Path(configured).expanduser().resolve()


def resolve_project_dir(project_dir: str | Path) -> Path:
    path = Path(project_dir).expanduser()
    if path.is_absolute():
        return path.resolve()
    root = workflow_root()
    if root is not None:
        return (root / path).resolve()
    return path.resolve()
