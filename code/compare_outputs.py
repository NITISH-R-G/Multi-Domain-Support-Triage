"""Compare two prediction CSVs to a labeled gold CSV (optional justification column).

Usage (from repo root or code/):

  python compare_outputs.py --gold support_tickets/sample_support_tickets.csv \\
      --pred support_tickets/sample_pred.csv

Uses the same merge keys as eval_sample (Issue, Subject, Company) and reports
token F1 / compact overlap for Response and Justification when gold columns exist.
"""
from __future__ import annotations

import argparse

import pandas as pd

from eval_metrics import compact_overlap_ratio, normalize_text, token_set_f1


def main() -> None:
    ap = argparse.ArgumentParser(description="Compare gold vs predicted CSV rows")
    ap.add_argument("--gold", type=str, required=True, help="CSV with expected columns")
    ap.add_argument("--pred", type=str, required=True, help="CSV with predictions (issue/subject/company lowercase)")
    args = ap.parse_args()

    gold = pd.read_csv(args.gold)
    pred = pd.read_csv(args.pred)
    pred = pred.rename(
        columns={
            "issue": "Issue",
            "subject": "Subject",
            "company": "Company",
            "response": "Pred_Response",
            "product_area": "Pred_Product Area",
            "status": "Pred_Status",
            "request_type": "Pred_Request Type",
            "justification": "Pred_Justification",
        }
    )
    keys = ["Issue", "Subject", "Company"]
    merged = gold.merge(pred, on=keys, how="inner")
    print(f"matched rows: {len(merged)} / gold {len(gold)} / pred {len(pred)}")
    if len(merged) == 0:
        return

    def block(title: str, gold_col: str, pred_col: str) -> None:
        if gold_col not in merged.columns or pred_col not in merged.columns:
            print(f"\n[{title}] skipped (missing {gold_col} or {pred_col})")
            return
        g = merged[gold_col].fillna("").astype(str)
        p = merged[pred_col].fillna("").astype(str)
        norm_eq = (g.map(normalize_text) == p.map(normalize_text)).mean()
        f1s = [token_set_f1(a, b) for a, b in zip(g, p)]
        ovs = [compact_overlap_ratio(a, b) for a, b in zip(g, p)]
        print(f"\n[{title}]")
        print(f"  normalized exact: {norm_eq:.2%}")
        print(f"  token F1 (mean):  {sum(f1s) / len(f1s):.3f}")
        print(f"  compact overlap:  {sum(ovs) / len(ovs):.3f}")

    block("Response", "Response", "Pred_Response")
    block("Justification", "Justification", "Pred_Justification")


if __name__ == "__main__":
    main()
