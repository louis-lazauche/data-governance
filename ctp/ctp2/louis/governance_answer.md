# CTP 2 - Which governance guard was missing at ShopFast?

ShopFast had no data contract between the payment producer and its consumers stating the unit of `amount` (EUR with 2 decimals, not cents), and no value-range or distribution check at ingestion, so a batch sent in cents passed every naive test (not null, unique, allowed values) and would have loaded silently into revenue.
