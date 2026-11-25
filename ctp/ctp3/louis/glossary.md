{% docs gross_revenue %}
**Gross revenue (EUR)** — total amount paid by the customer for an order, VAT included, shipping included, before refunds.
Owner: Head of Sales · Steward: Karim Benali · Status: approved (2026-11-10)
{% enddocs %}

{% docs net_revenue %}
**Net revenue (EUR)** — money ShopFast keeps from an order: what the customer paid, minus refunds, without VAT.

- **Formula:** `net_revenue_eur = round((gross_revenue_eur − refunded_eur) / 1.20, 2)` — shipping fees stay in; cancelled orders are excluded when net revenue is summed for a period.
- **Example:** €120.00 paid, no refund → (120 − 0) / 1.20 = **€100.00**. €120.00 paid, €60.00 refunded → **€50.00**.
- **Not to confuse with:** gross revenue (VAT included, before refunds), still used by Sales for commissions.
- Owner: Paul Girard (Head of Finance) · Steward: Karim Benali · Status: **approved (2026-11-25)**
{% enddocs %}

{% docs active_customer %}
**Active customer** — a customer account with at least one non-cancelled order in the last 12 months.

- **Formula:** `count(distinct customer_id) from fct_orders where status <> 'cancelled' and order_date > today − 12 months and order_date <= today`
- **Example:** on 2026-11-25, **1 080** of 1 233 accounts are active. A customer whose only order on 2026-03-02 was cancelled is **not** active.
- **Sales 6-month view:** a separate term, **recently active customer** (same rule over 6 months: 775 accounts on 2026-11-25), used only by the Sales dashboard and campaigns.
- Owner: Sara Martin (Head of Sales), aligned with Paul Girard (Finance) · Steward: Karim Benali · Status: **approved (2026-11-25)**
{% enddocs %}

{% docs churned_customer %}
**Churned customer** — a customer who has bought from ShopFast before but has no non-cancelled order in the last 12 months.

- **Formula:** has ≥ 1 non-cancelled order with `order_date <= today` AND is not an active customer.
- **Example:** on 2026-11-25, 1 225 accounts have bought at least once and 1 080 are active → **145** churned customers. An account that never ordered is not churned (it was never active).
- Owner: Sara Martin (Head of Sales) · Steward: Karim Benali · Status: **approved (2026-11-25)**
{% enddocs %}

{% docs customer %}
**Customer** — a person who has created an account on ShopFast, identified by one `customer_id`.

- **Rule:** one row of `dim_customers` = one account (exact duplicate rows removed). One person with two emails can still have two accounts; merging them is a Steward decision.
- **Example:** 1 241 raw rows − 8 exact duplicates = **1 233** customers.
- Owner: Sara Martin (Head of Sales) · Steward: Karim Benali · Status: **approved (2026-11-25)**
{% enddocs %}

{% docs order %}
**Order** — one purchase placed by a customer on one channel (web, mobile app, marketplace), identified by one `order_id`, whatever its status.

- **Rule:** one row of `fct_orders` = one order (duplicate `order_id` removed, first copy kept). Cancelled orders stay orders but are excluded from net revenue and from active customers.
- **Example:** 5 200 orders, of which 434 cancelled → **4 766** orders count for revenue.
- Owner: Sara Martin (Head of Sales) · Steward: Karim Benali · Status: **approved (2026-11-25)**
{% enddocs %}
