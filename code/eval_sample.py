from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from eval_metrics import compact_overlap_ratio, normalize_text, token_set_f1


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
    merged = sample.merge(pred, on=key_cols, how="inner").copy()

    print(f"sample rows: {len(sample)}")
    print(f"pred rows:   {len(pred)}")
    print(f"matched:    {len(merged)} (exact match on Issue+Subject+Company)")

    if len(merged) == 0:
        print("No exact matches found; check that output.csv is produced from sample vs support_tickets input.")
        return

    merged.loc[:, "Status"] = merged["Status"].map(_norm_status)
    merged.loc[:, "Pred_Status"] = merged["Pred_Status"].map(_norm_status)

    def exact_acc(gold: str, pred_col: str) -> float:
        g = merged[gold].fillna("").astype(str)
        p = merged[pred_col].fillna("").astype(str)
        return float((g == p).mean())

    print("\nExact match accuracy (on matched rows):")
    print(f"- status:       {exact_acc('Status', 'Pred_Status'):.2%}")
    print(f"- request_type: {exact_acc('Request Type', 'Pred_Request Type'):.2%}")
    print(f"- product_area: {exact_acc('Product Area', 'Pred_Product Area'):.2%}")

    print("\nAnswer columns (same rows; normalized exact + fuzzy):")
    ge = merged["Response"].fillna("").map(normalize_text)
    pe = merged["Pred_Response"].fillna("").map(normalize_text)
    je = merged["Justification"].fillna("").map(normalize_text) if "Justification" in merged.columns else None
    pje = merged["Pred_Justification"].fillna("").map(normalize_text) if "Pred_Justification" in merged.columns else None
    print(f"- response (norm exact):  {float((ge == pe).mean()):.2%}")
    if je is not None and pje is not None:
        print(f"- justification (norm exact): {float((je == pje).mean()):.2%}")
    f1_r = [token_set_f1(str(a), str(b)) for a, b in zip(merged["Response"], merged["Pred_Response"])]
    print(f"- response (token F1 mean):   {sum(f1_r) / max(1, len(f1_r)):.3f}")
    if "Justification" in merged.columns:
        f1_j = [
            token_set_f1(str(a), str(b)) for a, b in zip(merged["Justification"], merged["Pred_Justification"])
        ]
        print(f"- justification (token F1 mean): {sum(f1_j) / max(1, len(f1_j)):.3f}")
    ovl = [compact_overlap_ratio(str(a), str(b)) for a, b in zip(merged["Response"], merged["Pred_Response"])]
    print(f"- response (compact char overlap mean): {sum(ovl) / max(1, len(ovl)):.3f}")

    mism = merged[merged["Status"] != merged["Pred_Status"]][key_cols + ["Status", "Pred_Status"]]
    print(f"\nStatus mismatches: {len(mism)}")

    report_cols = key_cols + [
        "Status",
        "Pred_Status",
        "Request Type",
        "Pred_Request Type",
        "Product Area",
        "Pred_Product Area",
        "Response",
        "Pred_Response",
    ]
    if "Justification" in merged.columns:
        report_cols += ["Justification", "Pred_Justification"]
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    merged[report_cols].to_csv(args.report, index=False)
    print(f"Wrote report: {args.report}")


if __name__ == "__main__":
    main()

