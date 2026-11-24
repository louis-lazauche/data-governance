"""Replay openrefine_customers_recipe.json on the ORIGINAL customers.csv through the local OpenRefine API.
Start OpenRefine first (http://127.0.0.1:3333), then:  python replay_openrefine_recipe.py
Writes customers_clean.csv. Proves that the recipe replays on the raw file.
"""
import json, re, sys
import requests

OR = "http://127.0.0.1:3333"
RAW = "../shopfast-kit/data/customers.csv"
s = requests.Session()
token = lambda: s.get(f"{OR}/command/core/get-csrf-token").json()["token"]

options = {"separator": ",", "headerLines": 1, "guessCellValueTypes": False, "storeBlankCellsAsNulls": True,
           "processQuotes": True, "encoding": "UTF-8", "ignoreLines": -1, "skipDataLines": 0, "limit": -1}
with open(RAW, "rb") as f:
    r = s.post(f"{OR}/command/core/create-project-from-upload", params={"csrf_token": token()},
               files={"project-file": ("customers.csv", f, "text/csv")},
               data={"project-name": "ShopFast customers - CTP2 replay", "format": "text/line-based/*sv",
                     "options": json.dumps(options)}, allow_redirects=False)
project = re.search(r"project=(\d+)", r.headers.get("Location", "") + r.text).group(1)
print("Project created:", project)

recipe = json.load(open("openrefine_customers_recipe.json", encoding="utf-8"))
r = s.post(f"{OR}/command/core/apply-operations", params={"csrf_token": token()},
           data={"project": project, "operations": json.dumps(recipe)})
print("Apply recipe:", r.json())

r = s.post(f"{OR}/command/core/export-rows", params={"csrf_token": token()},
           data={"project": project, "format": "csv", "engine": json.dumps({"facets": [], "mode": "row-based"})})
r.encoding = "utf-8"
open("customers_clean.csv", "w", encoding="utf-8", newline="").write(r.text)
print("customers_clean.csv written:", r.text.count("\n") - 1, "rows")

hist = s.get(f"{OR}/command/core/get-operations", params={"project": project}).json()
for e in hist.get("entries", []):
    print(" -", e["description"])
print(f"Open the project: {OR}/project?project={project}")
