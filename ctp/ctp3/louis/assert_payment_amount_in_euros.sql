-- Contract on stg_payments.amount: EUROS with 2 decimals, never cents (CM 2 incident).
-- Fails (returns rows) if one amount is out of range, or if the batch average looks like cents.
select 'out_of_range' as problem, payment_id, amount
from {{ ref('stg_payments') }}
where amount <= 0 or amount > 2000
union all
select 'average_looks_like_cents' as problem, null as payment_id, avg(amount) as amount
from {{ ref('stg_payments') }}
having avg(amount) > 500
