"""CLI ``--help`` works when launched from ``code/`` (same as CI)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_CODE_DIR = Path(__file__).resolve().parents[1]


def test_main_py_help_from_code_directory() -> None:
    r = subprocess.run(
        [sys.executable, "main.py", "--help"],
        cwd=str(_CODE_DIR),
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    out = r.stdout + r.stderr
    assert "--input" in out or "--limit" in out.lower()
