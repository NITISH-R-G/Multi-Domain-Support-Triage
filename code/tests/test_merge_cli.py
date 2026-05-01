"""CLI exits when gold vs pred produce zero merge rows."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_CODE = Path(__file__).resolve().parents[1]


def test_eval_sample_exits_2_on_zero_merge(tmp_path: Path) -> None:
    gold = tmp_path / "g.csv"
    pred = tmp_path / "p.csv"
    gold.write_text(
        "Issue,Subject,Company,Response,Product Area,Status,Request Type\n"
        "sameissue,s,c,,,,",
        encoding="utf-8",
    )
    pred.write_text(
        "Issue,Subject,Company,response,status,product_area,request_type,justification\n"
        "different,s,c,,replied,,,",
        encoding="utf-8",
    )
    r = subprocess.run(
        [
            sys.executable,
            str(_CODE / "eval_sample.py"),
            "--sample",
            str(gold),
            "--pred",
            str(pred),
            "--report",
            str(tmp_path / "r.csv"),
        ],
        cwd=str(_CODE),
        capture_output=True,
        text=True,
    )
    assert r.returncode == 2
    assert "no rows matched" in r.stderr.lower()


def test_compare_outputs_exits_2_on_zero_merge(tmp_path: Path) -> None:
    gold = tmp_path / "g.csv"
    pred = tmp_path / "p.csv"
    gold.write_text("Issue,Subject,Company,Response\na,b,c,x\n", encoding="utf-8")
    pred.write_text("Issue,Subject,Company,response\nz,b,c,y\n", encoding="utf-8")
    r = subprocess.run(
        [
            sys.executable,
            str(_CODE / "compare_outputs.py"),
            "--gold",
            str(gold),
            "--pred",
            str(pred),
        ],
        cwd=str(_CODE),
        capture_output=True,
        text=True,
    )
    assert r.returncode == 2
    assert "no rows matched" in r.stderr.lower()
