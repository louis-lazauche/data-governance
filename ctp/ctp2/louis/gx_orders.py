"""CTP 2 - Exercise 3: build an expectation suite for ShopFast orders (GX Core 1.x).
Run from the 02_CTP2 folder:  python gx_orders.py
"""
import pandas as pd
import great_expectations as gx

KIT = "../shopfast-kit/data/"   # adapt if your kit is elsewhere
orders = pd.read_csv(KIT + "orders.csv", dtype=str)
customers = pd.read_csv(KIT + "customers.csv", dtype=str)
orders["total_amount_eur"] = pd.to_numeric(orders["total_amount_eur"], errors="coerce")
TODAY = pd.Timestamp("2026-11-25")   # date of the lab; use pd.Timestamp.today().normalize() in production
orders["order_date_dt"] = pd.to_datetime(orders["order_date"], format="%Y-%m-%d", errors="coerce")  # typed copy for range checks

context = gx.get_context(mode="file")                       # creates ./gx/ (config + Data Docs)
source = context.data_sources.add_or_update_pandas("shopfast")
asset = source.add_dataframe_asset(name="orders")
batch_def = asset.add_batch_definition_whole_dataframe("all_orders")

suite = context.suites.add_or_update(gx.ExpectationSuite(name="orders_suite"))
E = gx.expectations
for e in [
    E.ExpectTableRowCountToBeBetween(min_value=1000, max_value=100000),
    E.ExpectColumnValuesToNotBeNull(column="order_id"),
    E.ExpectColumnValuesToBeUnique(column="order_id"),
    # 1 (Completeness) every order belongs to someone
    E.ExpectColumnValuesToNotBeNull(column="customer_id"),
    # 2 (Consistency) referential integrity: the customer must exist in customers
    E.ExpectColumnValuesToBeInSet(column="customer_id", value_set=sorted(set(customers["customer_id"]))),
    # 3 (Completeness + Validity) order_date is filled and ISO formatted
    E.ExpectColumnValuesToNotBeNull(column="order_date"),
    E.ExpectColumnValuesToMatchRegex(column="order_date", regex=r"^\d{4}-\d{2}-\d{2}$"),
    # 4 (Timeliness / Accuracy) no order in the future, none before ShopFast's history starts (2025-01-01)
    E.ExpectColumnValuesToBeBetween(column="order_date_dt", min_value=pd.Timestamp("2025-01-01"), max_value=TODAY),
    # 5 (Validity) status only in the five business states (exact spelling, lower case)
    E.ExpectColumnValuesToBeInSet(column="status", value_set=["pending", "shipped", "delivered", "cancelled", "returned"]),
    # 6 (Validity) allowed values observed with value_counts(): 3 channels, 4 shipping countries
    E.ExpectColumnValuesToBeInSet(column="channel", value_set=["web", "mobile_app", "marketplace"]),
    E.ExpectColumnValuesToBeInSet(column="shipping_country", value_set=["FR", "BE", "DE", "ES"]),
    # 7 (Accuracy) amounts strictly positive and <= 2000 EUR: max observed is ~1400 EUR,
    #   so 2000 leaves headroom while still catching an amount sent in cents (x100)
    E.ExpectColumnValuesToBeBetween(column="total_amount_eur", min_value=0, max_value=2000, strict_min=True),
]:
    suite.add_expectation(e)
suite.save()

vd = context.validation_definitions.add_or_update(gx.ValidationDefinition(name="orders_validation", data=batch_def, suite=suite))
checkpoint = context.checkpoints.add_or_update(gx.Checkpoint(name="orders_checkpoint", validation_definitions=[vd],
                                                             actions=[gx.checkpoint.UpdateDataDocsAction(name="docs")]))
result = checkpoint.run(batch_parameters={"dataframe": orders})

print("\nSuite passed:", result.success)
for vr in result.run_results.values():
    for r in vr.results:
        cfg = r.expectation_config
        print(f"{'PASS' if r.success else 'FAIL'}  {cfg.type:<45} {cfg.kwargs.get('column', ''):<18} unexpected={r.result.get('unexpected_count', '-')}")
print("\nOpen the report: gx/uncommitted/data_docs/local_site/index.html")
