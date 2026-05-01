"""Ensure ``python -m code`` works from repository root (no ``cd code``)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]


def test_python_m_code_help_from_repo_root() -> None:
    r = subprocess.run(
        [sys.executable, "-m", "code", "--help"],
        cwd=str(_REPO),
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    out = r.stdout + r.stderr
    assert "--input" in out or "--limit" in out.lower()
