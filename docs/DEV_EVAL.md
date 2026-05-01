# Dev evaluation rubric (manual spot-check)

The platform scores **`response`** and **`justification`** on hidden rows. Public **`sample_support_tickets.csv`** does not include gold **justification**, so **automatic justification scoring is limited**. Use this rubric for **20–50 rows** you sample (from `sample_support_tickets.csv`, `support_tickets.csv`, or synthetic edge cases).

## How to run quantitative helpers

From **`code/`**:

```bash
python run_eval.py --offline
python compare_outputs.py --gold ../support_tickets/sample_support_tickets.csv --pred ../support_tickets/sample_pred.csv
```

Interpret **token F1 / overlap** as **smoke signals**, not hidden-test proxies.

## Blind rubric (1–5 per dimension)

For each sampled row, score **prediction vs corpus truth** without peeking at intermediate retrieval unless debugging:

| Dim | 1 | 3 | 5 |
|-----|---|---|---|
| **Grounding** | Introduces facts not in snippets/corpus | Mostly grounded | Fully grounded; cites sensible paths in justification |
| **Helpfulness** | Misleading or useless | Partially addresses ask | Actionable, matches ticket intent |
| **Tone** | Robotic / hostile | Neutral | Clear support tone |
| **Routing** | Wrong status/type/area | Mostly right | Matches intended handling |

**Target:** Average ≥ **3.5** on a diverse 20-row slice before you trust submission quality.

## Rows worth including

- One **Visa travel vs card loss** disambiguation  
- One **HackerRank community vs screen**  
- One **Claude privacy / delete conversation**  
- One **outage / bug** (`request_type=bug`)  
- One **invalid / gratitude**  
- One **ambiguous `Company=None`**  

Record scores in a spreadsheet; keep **version + git SHA** with the sheet for reproducibility.

## What “winning” still requires

Strong rubric scores **plus** good **interview** narrative — the codebase alone does not guarantee hidden-set wins.
