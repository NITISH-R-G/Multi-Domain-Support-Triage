from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _norm_status(x: object) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    s = str(x).strip().lower()
    if s in {"replied", "reply"}:
        return "replied"
    if s in {"escalated", "escalate"}:
        return "escalated"
    return s


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=str, default=str(Path("..") / "support_tickets" / "sample_support_tickets.csv"))
    ap.add_argument("--pred", type=str, default=str(Path("..") / "support_tickets" / "output.csv"))
    ap.add_argument("--report", type=str, default=str(Path("..") / "support_tickets" / "sample_eval_report.csv"))
    args = ap.parse_args()

    sample = pd.read_csv(args.sample)
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

    key_cols = ["Issue", "Subject", "Company"]
    merged = sample.merge(pred, on=key_cols, how="inner")

    print(f"sample rows: {len(sample)}")
    print(f"pred rows:   {len(pred)}")
    print(f"matched:    {len(merged)} (exact match on Issue+Subject+Company)")

    if len(merged) == 0:
        print("No exact matches found; check that output.csv is produced from sample vs support_tickets input.")
        return

    merged["Status"] = merged["Status"].map(_norm_status)
    merged["Pred_Status"] = merged["Pred_Status"].map(_norm_status)

    def exact_acc(gold: str, pred_col: str) -> float:
        g = merged[gold].fillna("").astype(str)
        p = merged[pred_col].fillna("").astype(str)
        return float((g == p).mean())

    print("\nExact match accuracy (on matched rows):")
    print(f"- status:       {exact_acc('Status', 'Pred_Status'):.2%}")
    print(f"- request_type: {exact_acc('Request Type', 'Pred_Request Type'):.2%}")
    print(f"- product_area: {exact_acc('Product Area', 'Pred_Product Area'):.2%}")

    mism = merged[merged["Status"] != merged["Pred_Status"]][key_cols + ["Status", "Pred_Status"]]
    print(f"\nStatus mismatches: {len(mism)}")

    report_cols = key_cols + [
        "Status",
        "Pred_Status",
        "Request Type",
        "Pred_Request Type",
        "Product Area",
        "Pred_Product Area",
    ]
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    merged[report_cols].to_csv(args.report, index=False)
    print(f"Wrote report: {args.report}")


if __name__ == "__main__":
    main()

