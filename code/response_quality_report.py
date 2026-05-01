"""Offline quality diagnostics for generated CSV outputs.

Computes cheap, interpretable metrics without needing hidden labels:
- response length (chars / words)
- escalation rate
- numeric-string leakage heuristic (digits sequences not present in retrieved evidence)
- lexical overlap between response tokens and retrieved chunk tokens (requires rebuilding retrieval hits)

This is meant for hackathon iteration: catch verbose outputs and grounding drift early.
"""
from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from config import CACHE_PATH, DATA_DIR, TOP_K
from corpus import tokenize
from grounding import has_unsupported_numbers, lexical_overlap
from retrieve import BM25Index, rerank_hits


def _norm_company(val: object) -> str | None:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).strip()
    if not s or s.lower() == "none":
        return None
    return s


def _brand_for_search(company: str | None, issue: str, subject: str, index: BM25Index) -> str:
    if company:
        m = company.strip().lower()
        if m == "hackerrank":
            return "hackerrank"
        if m == "claude":
            return "claude"
        if m == "visa":
            return "visa"
    return index.infer_brand(f"{subject}\n{issue}")


@dataclass(frozen=True)
class RowMetrics:
    overlap: float
    numeric_leak: bool


def metrics_for_row(index: BM25Index, issue: str, subject: str, company_raw: object, response: str) -> RowMetrics:
    company = _norm_company(company_raw)
    brand = _brand_for_search(company, issue, subject, index)
    hits, _raw_top = index.search(f"{subject}\n{issue}", brand, TOP_K)
    hits = rerank_hits(f"{subject}\n{issue}", hits)
    ov = lexical_overlap(response, hits) if hits else 0.0
    leak = has_unsupported_numbers(response, hits) if hits else False
    return RowMetrics(overlap=ov, numeric_leak=leak)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", type=str, default=str(Path("..") / "support_tickets" / "output.csv"))
    ap.add_argument("--offline", action="store_true", help="Force ORCHESTRATE_DISABLE_LLM=1 (informational; retrieval ignores it)")
    args = ap.parse_args()

    if args.offline:
        os.environ["ORCHESTRATE_DISABLE_LLM"] = "1"

    df = pd.read_csv(args.pred)
    norm_cols = {str(c).strip().lower(): c for c in df.columns}
    required = {"issue", "subject", "company", "response", "status"}
    missing = required - set(norm_cols.keys())
    if missing:
        raise SystemExit(f"CSV missing columns: {sorted(missing)}")
    issue_c = norm_cols["issue"]
    sub_c = norm_cols["subject"]
    comp_c = norm_cols["company"]
    resp_c = norm_cols["response"]
    stat_c = norm_cols["status"]

    index = BM25Index.load(CACHE_PATH, DATA_DIR)

    overlaps: list[float] = []
    leaks = 0
    lengths = []
    esc = 0

    for _, row in df.iterrows():
        issue = str(row.get(issue_c, "") or "")
        subject = str(row.get(sub_c, "") or "")
        resp = str(row.get(resp_c, "") or "")
        st = str(row.get(stat_c, "") or "").lower()
        if st == "escalated":
            esc += 1

        lengths.append(len(resp.split()))

        m = metrics_for_row(index, issue, subject, row.get(comp_c), resp)
        overlaps.append(m.overlap)
        if m.numeric_leak:
            leaks += 1

    n = max(1, len(df))
    print(f"rows: {len(df)}")
    print(f"escalated_rate: {esc/n:.2%}")
    print(f"avg_response_words: {sum(lengths)/n:.1f}")
    print(f"p95_response_words: {sorted(lengths)[int(0.95*(len(lengths)-1))] if lengths else 0}")
    print(f"avg_lexical_overlap: {sum(overlaps)/n:.3f}")
    print(f"p05_lexical_overlap: {sorted(overlaps)[0] if overlaps else 0.0}")
    print(f"numeric_leak_rows: {leaks} ({leaks/n:.2%})")


if __name__ == "__main__":
    main()
