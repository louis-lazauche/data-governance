# CTP 2 - Data quality (Louis)

| Deliverable | File |
|---|---|
| Quality scorecard (12 rules, 6 dimensions, severity, who fixes) | `quality_scorecard.csv` |
| Cleaned customers + replayable OpenRefine recipe | `customers_clean.csv`, `openrefine_customers_recipe.json` |
| Orders expectation suite (12 expectations) + Data Docs screenshots | `gx_orders.py`, `gx_orders_datadocs_*.png` |
| Payments: history passes, cents batch fails | `gx_payments.py` |
| Missing governance guard | `governance_answer.md` |

Reproduce (from the `02_CTP2` course folder, kit in `../shopfast-kit`, venv active):
- `python profile_customers.py` - measures every scorecard rule
- `python replay_openrefine_recipe.py` - replays the recipe on the raw `customers.csv` through OpenRefine (http://127.0.0.1:3333) and writes `customers_clean.csv`
- `python gx_orders.py` / `python gx_payments.py`
