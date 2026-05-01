from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_CODE = Path(__file__).resolve().parents[1]


def _run(args: list[str], *, cwd: Path = _CODE) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "main.py", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


def test_main_missing_input_exits_2() -> None:
    r = _run(["--input", "definitely_missing_file_orch.csv", "--output", "out.csv"])
    assert r.returncode == 2
    assert "not found" in (r.stderr + r.stdout).lower()
    assert "Traceback" not in r.stderr


def test_main_negative_limit_exits_2() -> None:
    r = _run(["--input", "nonexistent", "--limit", "-1"])
    assert r.returncode == 2
    assert "limit" in r.stderr.lower()


def test_main_help_exits_0() -> None:
    r = _run(["--help"])
    assert r.returncode == 0
    assert "limit" in r.stdout.lower()
