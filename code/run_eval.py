"""Convenience wrapper: regenerate preds for sample_support_tickets.csv and print eval_sample metrics."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Regenerate sample predictions and print eval_sample metrics (optional quality report).",
    )
    ap.add_argument("--offline", action="store_true", help="Force ORCHESTRATE_DISABLE_LLM=1 for repeatable runs")
    ap.add_argument(
        "--report-quality",
        action="store_true",
        help="Run response_quality_report.py on the generated sample_pred.csv",
    )
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    sample_in = root / "support_tickets" / "sample_support_tickets.csv"
    sample_out = root / "support_tickets" / "sample_pred.csv"
    report = root / "support_tickets" / "sample_eval_report.csv"

    env = dict(**os.environ)
    if args.offline:
        env["ORCHESTRATE_DISABLE_LLM"] = "1"

    steps: list[tuple[str, list[str]]] = [
        (
            "Generate predictions (main.py → sample_pred.csv)",
            [
                sys.executable,
                str(root / "code" / "main.py"),
                "--input",
                str(sample_in),
                "--output",
                str(sample_out),
            ],
        ),
        (
            "Compare to labeled sample (eval_sample.py)",
            [
                sys.executable,
                str(root / "code" / "eval_sample.py"),
                "--sample",
                str(sample_in),
                "--pred",
                str(sample_out),
                "--report",
                str(report),
            ],
        ),
    ]

    for label, cmd in steps:
        print(f"[run_eval] {label}", file=sys.stderr)
        r = subprocess.run(cmd, cwd=str(root / "code"), env=env)
        if r.returncode != 0:
            print(f"[run_eval] FAILED: {label} (exit {r.returncode})", file=sys.stderr)
            raise SystemExit(r.returncode)

    if args.report_quality:
        label = "Quality report (response_quality_report.py)"
        cmd = [
            sys.executable,
            str(root / "code" / "response_quality_report.py"),
            "--pred",
            str(sample_out),
            "--offline",
        ]
        print(f"[run_eval] {label}", file=sys.stderr)
        r = subprocess.run(cmd, cwd=str(root / "code"), env=env)
        if r.returncode != 0:
            print(f"[run_eval] FAILED: {label} (exit {r.returncode})", file=sys.stderr)
            raise SystemExit(r.returncode)


if __name__ == "__main__":
    main()
