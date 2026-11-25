# CTP 3 - Catalog, lineage & glossary (Louis)

Project: `03_CTP3/shopfast_dbt` (dbt 1.12 + DuckDB). `dbt build` -> PASS=32, WARN=1 (14 orders with an unknown customer, test set to warn), ERROR=0.

| # | Deliverable | File(s) |
|---|---|---|
| 1 | Documented, owned and classified models - check PASSED | `_staging.yml`, `_marts.yml`, `check_governance_output.txt` |
| 2 | 3 exposures + impact note | `exposures.yml`, `impact_payments_cents.md` |
| 3 | Glossary (5 terms) + docs blocks linked with `doc()` | `glossary_template.csv`, `glossary.md` |
| 4 | Data dictionary, 15 columns of orders and payments | `data_dictionary_template.csv` |
| + | Test that blocks a batch in cents | `assert_payment_amount_in_euros.sql` (goes in `shopfast_dbt/tests/`) |
| + | Dictionary generated from the YAML (bonus) | `data_dictionary_from_dbt.csv` |

## check_governance.py

```
Models: 7 | documented columns: 58/58
GOVERNANCE CHECK: PASSED
```

## Choices

- **PII classification:** `internal` = pseudonymous id (customer_id); `confidential` = identifies a person (names, email, phone, city, marketing consent); `restricted` = sensitive/regulated (birth_date, card_last4 - PCI DSS).
- **Owners:** Sara Martin (Head of Sales) owns customer, order and product models; Paul Girard (Head of Finance) owns `stg_payments`; Karim Benali (Analytics Engineer) is steward everywhere.
- **Active customer conflict:** company definition = 12 months, non-cancelled orders (Finance rule, comparable year on year). Sales keeps a separate term *recently active customer* (6 months). Net revenue is always excluding VAT; Sales uses *gross revenue* (VAT incl.) for commissions.
- **Lineage:** `dbt ls --select source:shopfast_raw.payments+` -> stg_payments -> fct_orders -> dim_customers -> 3 exposures (Sales dashboard, Finance report, churn model).
