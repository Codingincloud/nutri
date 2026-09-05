"""
build_dataset_fixed.py
-----------------------
Drop-in replacement for build_dataset.py.

Fixes vs. the original:
1. is_nepali is derived from `category`, not hardcoded True.
2. is_vegetarian/is_vegan/is_gluten_free/contains_* are derived from the
   actual ingredient list via ingredient_tags.classify_recipe(), not
   hardcoded defaults.
3. fiber / sugar / sodium are NEVER silently written as 0. If your
   usda_ingredients.json entry doesn't have real values for these fields,
   the row is written with an empty value AND flagged in
   needs_manual_review.csv. Do not fill these with 0 -- 0 sugar/sodium
   directly defeats the diabetes/hypertension clinical safety filters
   described in the project README.
4. Any ingredient whose macro profile was produced by the old "equal split
   of dish total" estimation trick (i.e. is missing a `verified: true` tag)
   is flagged so the whole dish is routed to manual review instead of
   silently entering the production dataset.
"""

import json
import csv
import os
from ingredient_tags import classify_recipe, is_nepali_from_category


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("Starting corrected data pipeline...")

    usda = load_json("usda_ingredients.json")
    recipes = load_json("recipes.json")

    headers = [
        "food_id", "name", "name_nepali", "category", "calories", "protein",
        "carbohydrates", "fat", "fiber", "sugar", "sodium", "serving_size_g",
        "is_vegetarian", "is_vegan", "is_gluten_free", "contains_nuts",
        "contains_dairy", "contains_gluten", "contains_egg", "is_nepali",
        "data_source", "needs_manual_review", "review_reason",
    ]

    food_id = 1
    rows = []
    review_rows = []

    for recipe_name, details in recipes.items():
        total_calories = total_protein = total_carbs = total_fat = 0.0
        total_fiber = total_sugar = total_sodium = 0.0
        total_weight_g = 0.0

        missing_fiber_sugar_sodium = False
        unverified_ingredient_used = False
        ingredient_keys = list(details.get("ingredients", {}).keys())

        for ing_name, amount_g in details.get("ingredients", {}).items():
            if ing_name not in usda:
                print(f"Warning: '{ing_name}' not in USDA DB. Skipping ingredient.")
                unverified_ingredient_used = True
                continue

            base = usda[ing_name]
            multiplier = amount_g / 100.0

            total_calories += base.get("calories", 0) * multiplier
            total_protein += base.get("protein", 0) * multiplier
            total_carbs += base.get("carbs", 0) * multiplier
            total_fat += base.get("fat", 0) * multiplier
            total_weight_g += amount_g

            # Only accumulate fiber/sugar/sodium if the ingredient record
            # actually has them -- never assume 0.
            if "fiber" in base and "sugar" in base and "sodium" in base:
                total_fiber += base["fiber"] * multiplier
                total_sugar += base["sugar"] * multiplier
                total_sodium += base["sodium"] * multiplier
            else:
                missing_fiber_sugar_sodium = True

            # If this ingredient's profile was produced by the old
            # equal-split estimator rather than a verified lookup, flag it.
            if not base.get("verified", False):
                unverified_ingredient_used = True

        serving_size = round(total_weight_g) or 100

        flags = classify_recipe(ingredient_keys)
        category = details.get("category", "nepali_staple")

        row = {
            "food_id": food_id,
            "name": recipe_name,
            "name_nepali": details.get("name_nepali", recipe_name),
            "category": category,
            "calories": round(total_calories, 1),
            "protein": round(total_protein, 1),
            "carbohydrates": round(total_carbs, 1),
            "fat": round(total_fat, 1),
            "fiber": "" if missing_fiber_sugar_sodium else round(total_fiber, 1),
            "sugar": "" if missing_fiber_sugar_sodium else round(total_sugar, 1),
            "sodium": "" if missing_fiber_sugar_sodium else round(total_sodium, 1),
            "serving_size_g": serving_size,
            "is_vegetarian": flags["is_vegetarian"],
            "is_vegan": flags["is_vegan"],
            "is_gluten_free": flags["is_gluten_free"],
            "contains_nuts": flags["contains_nuts"],
            "contains_dairy": flags["contains_dairy"],
            "contains_gluten": flags["contains_gluten"],
            "contains_egg": flags["contains_egg"],
            "is_nepali": is_nepali_from_category(category),
            "data_source": "Calculated_from_USDA_verified" if not unverified_ingredient_used else "NEEDS_REVIEW",
            "needs_manual_review": missing_fiber_sugar_sodium or unverified_ingredient_used,
            "review_reason": "; ".join(filter(None, [
                "missing fiber/sugar/sodium data" if missing_fiber_sugar_sodium else "",
                "used unverified/estimated ingredient value" if unverified_ingredient_used else "",
            ])),
        }
        rows.append(row)
        if row["needs_manual_review"]:
            review_rows.append(row)
        food_id += 1

    os.makedirs("output", exist_ok=True)
    with open("output/nepali_foods_derived_fixed.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    with open("output/needs_manual_review.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(review_rows)

    print(f"Wrote {len(rows)} rows to output/nepali_foods_derived_fixed.csv")
    print(f"{len(review_rows)} of {len(rows)} rows need manual nutrition verification "
          f"before they should be trusted -- see output/needs_manual_review.csv")


if __name__ == "__main__":
    main()
