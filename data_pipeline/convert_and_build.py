import json
import csv
import os
import re

def parse_num(val):
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        match = re.search(r'([\d\.]+)', val)
        if match:
            return float(match.group(1))
    return 0.0

def main():
    print("=== Automated Pipeline Converter & Builder ===")
    
    clean_pasted_path = 'clean_pasted_foods.json'
    recipes_path = 'recipes.json'
    usda_path = 'usda_ingredients.json'
    
    if not os.path.exists(clean_pasted_path):
        print(f"Error: {clean_pasted_path} not found.")
        return

    with open(clean_pasted_path, 'r', encoding='utf-8') as f:
        pasted_foods = json.load(f)
        
    print(f"Loaded {len(pasted_foods)} pasted foods.")

    # Load or init usda_ingredients
    usda = {}
    if os.path.exists(usda_path):
        with open(usda_path, 'r', encoding='utf-8') as f:
            usda = json.load(f)

    # Load or init recipes
    recipes = {}
    if os.path.exists(recipes_path):
        with open(recipes_path, 'r', encoding='utf-8') as f:
            recipes = json.load(f)

    # Convert pasted foods into recipes & USDA ingredient composition
    count = 0
    for food in pasted_foods:
        name = food.get('food_name', '').strip()
        if not name or name in recipes:
            continue
            
        calories = parse_num(food.get('food_calories_per_serving', 0))
        nutr = food.get('food_nutritional_factors', {})
        carbs = parse_num(nutr.get('carbohydrates', 0))
        protein = parse_num(nutr.get('protein', 0))
        fat = parse_num(nutr.get('fat', 0))
        
        ingredients = food.get('food_ingredients', [])
        cuisine = food.get('cuisine_type', 'Global')
        
        # Build recipe ingredient entries
        ing_dict = {}
        if ingredients:
            portion_per_ing = max(10, round(150 / len(ingredients)))
            for ing in ingredients:
                ing_key = ing.lower().replace(' ', '_')
                ing_dict[ing_key] = portion_per_ing
                
                # If ingredient not in USDA, estimate baseline per 100g based on overall dish macros
                if ing_key not in usda:
                    multiplier = 100.0 / (len(ingredients) * portion_per_ing) if (len(ingredients) * portion_per_ing) > 0 else 1.0
                    usda[ing_key] = {
                        "calories": round(calories * multiplier, 1),
                        "protein": round(protein * multiplier, 1),
                        "carbs": round(carbs * multiplier, 1),
                        "fat": round(fat * multiplier, 1)
                    }
        else:
            ing_key = name.lower().replace(' ', '_') + '_base'
            ing_dict[ing_key] = 100
            if ing_key not in usda:
                usda[ing_key] = {
                    "calories": calories,
                    "protein": protein,
                    "carbs": carbs,
                    "fat": fat
                }

        is_veg = True if food.get('food_features', {}).get('taste') != 'savory meat' and 'chicken' not in name.lower() and 'pork' not in name.lower() and 'beef' not in name.lower() else False

        recipes[name] = {
            "ingredients": ing_dict,
            "cuisine": cuisine,
            "is_veg": is_veg,
            "category": food.get('cuisine_type', 'global').lower() + '_dish'
        }
        count += 1

    print(f"Added {count} new recipes into recipes.json.")

    # Save updated json files
    with open(usda_path, 'w', encoding='utf-8') as f:
        json.dump(usda, f, indent=2)
        
    with open(recipes_path, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, indent=2)

    print("Updated recipes.json and usda_ingredients.json.")

    # Run build_dataset.py logic to create final dataset CSV
    import build_dataset
    build_dataset.main()

if __name__ == '__main__':
    main()
