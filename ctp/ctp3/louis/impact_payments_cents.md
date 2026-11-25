# Impact note - payments team switches `amount` to cents

1. **What breaks:** `source:shopfast_raw.payments` -> `stg_payments.amount` -> `fct_orders.refunded_eur` and `net_revenue_eur` (refunds 100x too big, net revenue very negative) -> `dim_customers.lifetime_net_revenue_eur`.
2. **Who is affected:** all 3 exposures - Sales dashboard (Sara Martin, read daily by the CEO), Finance monthly revenue report (Paul Girard, board + annual accounts), churn prediction model (Karim Benali, retention campaigns).
3. **Owners to warn before the change:** Paul Girard (owner of `stg_payments`), Sara Martin (owner of `fct_orders` and `dim_customers`), Karim Benali (steward + churn model owner) - full list from `dbt ls --select source:shopfast_raw.payments+`.
4. **Test to add:** `tests/assert_payment_amount_in_euros.sql` (0 < amount <= 2000 and batch average <= 500) stops the build, and `amount` is documented as "EUROS with 2 decimals, NOT cents" in `_staging.yml`.
5. **Who approves:** Paul Girard (Head of Finance, owner of payment data) approves the new unit and the switch date; no switch until `stg_payments` divides by 100 and `dbt build` is green.
