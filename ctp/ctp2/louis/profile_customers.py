"""CTP 2 - Exercise 1: profile customers.csv with pandas (completed starter).
Run from the 02_CTP2 folder:  python profile_customers.py
Prints one line per rule (failing rows, total, score) to copy into quality_scorecard.csv
"""
import pandas as pd

KIT = "../shopfast-kit/data/"
df = pd.read_csv(KIT + "customers.csv", dtype=str)   # dtype=str: keep the raw text (e.g. 01300)
orders = pd.read_csv(KIT + "orders.csv", dtype=str)
n = len(df)
TODAY = pd.Timestamp("2026-11-25")
print("Rows:", n)

rules = []  # (dimension, rule, failing_rows, total_rows)

def rule(dimension, name, failing, total):
    failing, total = int(failing), int(total)
    rules.append((dimension, name, failing, total))

# --- Completeness ---
print("\nEmpty values per column:\n", df.isna().sum())
rule("Completeness", "email is filled", df["email"].isna().sum(), n)
rule("Completeness", "phone is filled", df["phone"].isna().sum(), n)

# --- Uniqueness ---
rule("Uniqueness", "customer_id is unique (rows involved in a duplicate)", df["customer_id"].duplicated(keep=False).sum(), n)
# TODO 1: normalise email (strip + lower case) and count people registered twice
email_norm = df["email"].str.strip().str.lower()
dup_email = email_norm.notna() & email_norm.duplicated(keep="first")
# do not count exact duplicate rows twice: they are already caught by the customer_id rule
dup_people = dup_email & ~df.duplicated(keep="first")
rule("Uniqueness", "one customer per email (same person registered twice with a new id)", dup_people.sum(), n)

# --- Validity ---
# TODO 2: emails that do not match the regex
filled = df["email"].dropna().str.strip()
bad_email = ~filled.str.match(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")
print("\nInvalid emails:", list(filled[bad_email]))
rule("Validity", "email has the form name@domain.tld", bad_email.sum(), len(filled))
# TODO 5: loyalty_tier outside bronze / silver / gold / platinum
tiers = {"bronze", "silver", "gold", "platinum"}
print("\nloyalty_tier:\n", df["loyalty_tier"].value_counts())
rule("Validity", "loyalty_tier in bronze/silver/gold/platinum", (~df["loyalty_tier"].isin(tiers)).sum(), n)
# TODO 7: French postal codes that do not have 5 digits
country_iso = df["country"].str.strip().str.upper().replace(
    {"FRANCE": "FR", "FRA": "FR", "SPAIN": "ES", "ESPAGNE": "ES", "GERMANY": "DE", "ALLEMAGNE": "DE", "DEU": "DE",
     "BELGIUM": "BE", "BELGIQUE": "BE", "BEL": "BE"})
fr = df[country_iso == "FR"]
rule("Validity", "French postal_code has 5 digits", (~fr["postal_code"].str.fullmatch(r"\d{5}")).sum(), len(fr))

# --- Consistency ---
# TODO 3: distinct values of country
print("\ncountry:\n", df["country"].value_counts(dropna=False))
print("Spellings for 4 countries:", df["country"].nunique())
filled_c = df["country"].dropna()
rule("Consistency", "country is an ISO-2 code FR/BE/DE/ES", (~filled_c.isin(["FR", "BE", "DE", "ES"])).sum(), len(filled_c))
# TODO 4: signup_date values NOT in the format YYYY-MM-DD
rule("Consistency", "signup_date in format YYYY-MM-DD", (~df["signup_date"].str.fullmatch(r"\d{4}-\d{2}-\d{2}")).sum(), n)

# --- Accuracy ---
# TODO 6: birth dates in the future or before 1906 (ISO ones only, as asked)
iso = df["birth_date"].where(df["birth_date"].str.fullmatch(r"\d{4}-\d{2}-\d{2}"))
bd = pd.to_datetime(iso, format="%Y-%m-%d", errors="coerce")
bad_bd = (bd > TODAY) | (bd < "1906-01-01")
print("\nImpossible birth dates (ISO):", list(df.loc[bad_bd, "birth_date"]))
rule("Accuracy", "birth_date between 1906-01-01 and today (ISO dates)", bad_bd.sum(), bd.notna().sum())

# --- Timeliness (orders: the customers file has no load timestamp) ---
od = pd.to_datetime(orders["order_date"], format="%Y-%m-%d", errors="coerce")
rule("Timeliness", "orders.order_date is filled and not in the future", (od.isna() | (od > TODAY)).sum(), len(orders))

# Bonus: score_pct
print(f"\n{'dimension':<13} {'failing':>7} {'total':>6} {'score':>7}  rule")
for dim, name, failing, total in rules:
    print(f"{dim:<13} {failing:>7} {total:>6} {100 * (1 - failing / total):>6.2f}%  {name}")
