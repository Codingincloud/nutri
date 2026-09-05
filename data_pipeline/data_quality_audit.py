"""
data_quality_audit.py
----------------------
Run this against usda_ingredients.json, recipes.json, and the final CSV
any time the pipeline runs. It won't fix anything -- it just refuses to
let these specific failure modes slide through silently again.

Usage:
    python data_quality_audit.py
"""

import json
import csv
import os
from collections import Counter


def audit_usda_ingredients(path="usda_ingredients.json"):
    print(f"\n=== Auditing {path} ===")
    d = json.load(open(path, encoding="utf-8"))
    value_tuples = Counter()
    for k, v in d.items():
        t = (v.get("calories"), v.get("protein"), v.get("carbs"), v.get("fat"))
        value_tuples[t] += 1

    dupes = {t: c for t, c in value_tuples.items() if c > 1}
    affected = sum(dupes.values())
    print(f"Total ingredients: {len(d)}")
    print(f"Ingredients sharing a duplicate value-tuple with another ingredient: "
          f"{affected} ({affected/len(d):.0%})")
    if affected:
        print("  -> These are almost certainly fabricated via equal-split estimation, "
              "not real per-ingredient lookups. Re-source from real USDA data before use.")
        worst = sorted(dupes.items(), key=lambda x: -x[1])[:5]
        for t, c in worst:
            names = [k for k, v in d.items()
                     if (v.get("calories"), v.get("protein"), v.get("carbs"), v.get("fat")) == t]
            print(f"    {c}x identical {t}: {names}")

    unverified = [k for k, v in d.items() if not v.get("verified", False)]
    print(f"Ingredients missing an explicit 'verified: true' tag: {len(unverified)}")
    return dupes


def audit_recipes(path="recipes.json"):
    print(f"\n=== Auditing {path} ===")
    d = json.load(open(path, encoding="utf-8"))
    no_ingredients = [k for k, v in d.items() if not v.get("ingredients")]
    print(f"Recipes with zero ingredients listed: {len(no_ingredients)} {no_ingredients[:5]}")
    return d


def audit_source_json(path):
    print(f"\n=== Auditing raw source file: {path} ===")
    try:
        d = json.load(open(path, encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"  FILE IS NOT VALID JSON ({e}). This file likely still contains "
              f"pasted chat scaffolding (e.g. '<USER_REQUEST>' tags or truncation "
              f"notices) and should not be used as a data source at all.")
        return
    if isinstance(d, list):
        ids = [x.get("food_id") for x in d if "food_id" in x]
        non_int_ids = [i for i in ids if not isinstance(i, int)]
        print(f"Non-integer food_id values: {len(non_int_ids)} -- e.g. {non_int_ids[:5]}")
        names = Counter(x.get("food_name", "").strip() for x in d)
        dupe_names = {k: v for k, v in names.items() if v > 1 and k}
        print(f"Duplicate food_name entries: {len(dupe_names)}")
        for name, count in list(dupe_names.items())[:5]:
            cals = [x["food_calories_per_serving"] for x in d if x.get("food_name") == name]
            print(f"    '{name}' appears {count}x with conflicting calorie values: {cals}")


def audit_final_csv(path):
    print(f"\n=== Auditing final CSV: {path} ===")
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"Total rows: {len(rows)}")

    is_nepali_true = sum(1 for r in rows if r.get("is_nepali") == "True")
    print(f"Rows flagged is_nepali=True: {is_nepali_true} ({is_nepali_true/len(rows):.0%})")

    zero_sugar_sodium = sum(1 for r in rows if r.get("sugar") == "0" and r.get("sodium") == "0")
    print(f"Rows with sugar=0 AND sodium=0 (suspicious -- verify these are real, not defaults): "
          f"{zero_sugar_sodium}")

    # scaling sanity check: for USDA rows with serving_size != 100,
    # flag ones whose calories look identical to a typical raw per-100g figure
    scale_suspects = []
    for r in rows:
        try:
            serving = float(r.get("serving_size_g", 0))
            cal = float(r.get("calories", 0))
        except ValueError:
            continue
        if serving and abs(serving - 100) > 1 and cal > 400 and serving < 50:
            scale_suspects.append((r["name"], serving, cal))
    print(f"Rows that look like un-rescaled per-100g values on a small serving size: "
          f"{len(scale_suspects)} -- {scale_suspects[:5]}")

    names = Counter(r["name"].strip().lower() for r in rows)
    dupes = {k: v for k, v in names.items() if v > 1}
    print(f"Duplicate names in final CSV: {len(dupes)}")


if __name__ == "__main__":
    audit_usda_ingredients()
    audit_recipes()
    clean_json = "clean_pasted_foods.json" if os.path.exists("clean_pasted_foods.json") else "deprecated/clean_pasted_foods.json"
    if os.path.exists(clean_json):
        audit_source_json(clean_json)
    csv_path = "nepali_food_data.csv" if os.path.exists("nepali_food_data.csv") else "../backend/data/nepali_food_data.csv"
    audit_final_csv(csv_path)
