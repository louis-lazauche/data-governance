"""CTP 2 - Exercise 4: replay the 'cents' incident.
A naive suite (not null / unique / allowed values) PASSES on payments_batch_2.csv although every amount is 100x too big.
Only value-range and distribution expectations catch it.
"""
import pandas as pd
import great_expectations as gx

KIT = "../shopfast-kit/data/"
files = {"payments (history)": KIT + "payments.csv", "payments_batch_2 (new)": "payments_batch_2.csv"}

context = gx.get_context(mode="file")
source = context.data_sources.add_or_update_pandas("shopfast_payments")
asset = source.add_dataframe_asset(name="payments")
batch_def = asset.add_batch_definition_whole_dataframe("whole")
E = gx.expectations

naive = [E.ExpectColumnValuesToNotBeNull(column="payment_id"), E.ExpectColumnValuesToBeUnique(column="payment_id"),
         E.ExpectColumnValuesToNotBeNull(column="amount"), E.ExpectColumnValuesToBeInSet(column="currency", value_set=["EUR"]),
         E.ExpectColumnValuesToBeInSet(column="method", value_set=["card", "paypal", "apple_pay", "bank_transfer"])]
smart = naive + [
    # Thresholds calibrated on the history (payments.csv): min 13.70, max 1400.79, mean 235.92, median 184.31 EUR.
    # 1 (Accuracy, row level) a single payment is > 0 and <= 2000 EUR (same cap as orders.total_amount_eur)
    E.ExpectColumnValuesToBeBetween(column="amount", min_value=0, max_value=2000, strict_min=True),
    # 2 (Accuracy, batch level) the average basket stays in a realistic band; x100 moves it far out
    E.ExpectColumnMeanToBeBetween(column="amount", min_value=50, max_value=500),
    # 3 (Accuracy, batch level) the median resists outliers, so it only moves if the whole batch changed unit
    E.ExpectColumnMedianToBeBetween(column="amount", min_value=50, max_value=400),
    # 4 (Validity) euro amounts are written with a decimal point (217.38, 49.8); cents arrive as integers (21738)
    E.ExpectColumnValuesToMatchRegex(column="amount_txt", regex=r"^\d+\.\d{1,2}$", mostly=0.95),
]

def run(name, expectations, df):
    suite = context.suites.add_or_update(gx.ExpectationSuite(name=name))
    for e in expectations: suite.add_expectation(e.copy() if hasattr(e, "copy") else e)
    suite.save()
    return batch_def.get_batch(batch_parameters={"dataframe": df}).validate(suite)

for label, path in files.items():
    df = pd.read_csv(path, dtype=str); df["amount_txt"] = df["amount"]; df["amount"] = pd.to_numeric(df["amount"])
    for suite_name, exps in [("naive_payments", naive), ("smart_payments", smart)]:
        res = run(suite_name, exps, df)
        failed = [r.expectation_config.type for r in res.results if not r.success]
        print(f"{label:<24} {suite_name:<15} success={res.success}  failed={failed}")
