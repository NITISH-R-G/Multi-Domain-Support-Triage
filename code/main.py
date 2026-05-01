"""Offline-grounded support triage agent — entry point."""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from config import DATA_DIR, INPUT_CSV, OUTPUT_CSV, SEED, TOP_K
from csv_io import TicketCsvError, canonicalize_ticket_columns, read_tickets_csv
from openai_agent import decide_with_openai, fallback_from_hits
from postprocess import finalize_decision
from retrieve import BM25Index, CACHE_PATH, rerank_hits, should_escalate_low_retrieval
from risk import assess_risk
from taxonomy import looks_like_invalid_small_talk
from ticket_hints import maybe_append_multi_topic_justification

random.seed(SEED)
np.random.seed(SEED)


def _normalize_company(val: Any) -> str | None:
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


def _validate_row(d: dict[str, Any]) -> dict[str, Any]:
    status = str(d.get("status", "escalated")).lower()
    if status not in ("replied", "escalated"):
        status = "escalated"
    rt = str(d.get("request_type", "product_issue")).lower()
    if rt not in ("product_issue", "feature_request", "bug", "invalid"):
        rt = "product_issue"
    out = {
        "status": status,
        "product_area": str(d.get("product_area", "") or ""),
        "response": str(d.get("response", "") or ""),
        "justification": str(d.get("justification", "") or ""),
        "request_type": rt,
    }
    return out


def process_row(row: pd.Series, index: BM25Index) -> dict[str, Any]:
    issue = str(row.get("Issue", "") or "")
    subject = str(row.get("Subject", "") or "")
    company_raw = row.get("Company")

    company = _normalize_company(company_raw)
    brand = _brand_for_search(company, issue, subject, index)

    # Fast invalid handling (spam / gratitude / off-topic trivia).
    if looks_like_invalid_small_talk(subject, issue):
        decision = finalize_decision(
            brand=brand,
            issue=issue,
            subject=subject,
            hits=[],
            decision={
                "status": "replied",
                "product_area": "",
                "response": "I’m sorry, this is out of scope from my capabilities.",
                "justification": "Detected off-topic/invalid request.",
                "request_type": "invalid",
            },
            low_retrieval=False,
        )
        decision = maybe_append_multi_topic_justification(decision, issue=issue, subject=subject)
        return _validate_row(decision)

    hit = assess_risk(issue, subject)
    if hit:
        fb = fallback_from_hits([], escalated=True, esc_reason=hit.reason, low_retrieval=False)
        if hit.force_request_type:
            fb["request_type"] = hit.force_request_type
        return _validate_row(fb)

    hits, raw_top_score = index.search(f"{subject}\n{issue}", brand, TOP_K)
    hits = rerank_hits(f"{subject}\n{issue}", hits)
    low = should_escalate_low_retrieval(raw_top_score)

    decision = decide_with_openai(
        issue,
        subject,
        company_raw if company_raw is not None and not pd.isna(company_raw) else "None",
        hits,
        force_escalate_reason=None,
        low_retrieval=low,
    )
    decision = finalize_decision(
        brand=brand,
        issue=issue,
        subject=subject,
        hits=hits,
        decision=decision,
        low_retrieval=low,
    )
    decision = maybe_append_multi_topic_justification(decision, issue=issue, subject=subject)
    return _validate_row(decision)


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-domain support triage agent (Orchestrate)")
    parser.add_argument("--input", type=str, default=str(INPUT_CSV))
    parser.add_argument("--output", type=str, default=str(OUTPUT_CSV))
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        metavar="N",
        help="Process only the first N rows (default 0 = all rows). Must be >= 0.",
    )
    args = parser.parse_args()

    if args.limit < 0:
        print("error: --limit must be >= 0 (use 0 to process every row).", file=sys.stderr)
        sys.exit(2)

    out_p = Path(args.output).expanduser().resolve()
    out_p.parent.mkdir(parents=True, exist_ok=True)

    try:
        df = read_tickets_csv(args.input, label="--input")
        df = canonicalize_ticket_columns(df)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)
    except TicketCsvError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)

    n_all = len(df)
    if args.limit > 0:
        df = df.head(args.limit)
        print(
            f"Note: --limit {args.limit}: processing {len(df)} row(s) of {n_all} in the input file.",
            file=sys.stderr,
        )
    if not DATA_DIR.is_dir():
        print(f"error: corpus directory not found: {DATA_DIR}", file=sys.stderr)
        sys.exit(2)

    try:
        index = BM25Index.load(CACHE_PATH, DATA_DIR)
    except TimeoutError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)

    rows_out: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        pred = process_row(row, index)
        rows_out.append(
            {
                "issue": row.get("Issue", ""),
                "subject": row.get("Subject", ""),
                "company": row.get("Company", ""),
                "response": pred["response"],
                "product_area": pred["product_area"],
                "status": pred["status"],
                "request_type": pred["request_type"],
                "justification": pred["justification"],
            }
        )

    out_df = pd.DataFrame(rows_out)
    try:
        out_df.to_csv(out_p, index=False, encoding="utf-8")
    except OSError as e:
        print(f"error: cannot write --output {out_p}: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"Wrote {len(out_df)} rows to {out_p}", file=sys.stderr)


if __name__ == "__main__":
    main()
