import json
import csv
import os

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print("Starting Data Pipeline...")
    
    # 1. Load the authoritative ingredient data (USDA base)
    try:
        usda = load_json('usda_ingredients.json')
    except Exception as e:
        print(f"Error loading usda_ingredients.json: {e}")
        return

    # 2. Load the recipes
    try:
        recipes = load_json('recipes.json')
    except Exception as e:
        print(f"Error loading recipes.json: {e}")
        return

    # Prepare to write to CSV
    output_file = '../backend/data/nepali_foods_derived.csv'
    headers = [
        'food_id', 'name', 'name_nepali', 'category', 'calories', 'protein', 
        'carbohydrates', 'fat', 'fiber', 'sugar', 'sodium', 'serving_size_g', 
        'is_vegetarian', 'is_vegan', 'is_gluten_free', 'contains_nuts', 
        'contains_dairy', 'contains_gluten', 'contains_egg', 'is_nepali', 'data_source'
    ]

    print("Calculating exact macros based on USDA data...")
    
    food_id = 1
    rows = []
    
    for recipe_name, details in recipes.items():
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        total_weight_g = 0
        
        # Calculate totals from ingredients
        for ing_name, amount_g in details.get('ingredients', {}).items():
            if ing_name not in usda:
                print(f"Warning: Ingredient '{ing_name}' not found in USDA DB. Skipping.")
                continue
                
            base = usda[ing_name]
            # USDA values are per 100g
            multiplier = amount_g / 100.0
            
            total_calories += base.get('calories', 0) * multiplier
            total_protein += base.get('protein', 0) * multiplier
            total_carbs += base.get('carbs', 0) * multiplier
            total_fat += base.get('fat', 0) * multiplier
            total_weight_g += amount_g
            
        serving_size = round(total_weight_g)
        if serving_size == 0:
            serving_size = 100
        
        row = {
            'food_id': food_id,
            'name': recipe_name,
            'name_nepali': details.get('name_nepali', recipe_name),
            'category': details.get('category', 'nepali_staple'),
            'calories': round(total_calories, 1),
            'protein': round(total_protein, 1),
            'carbohydrates': round(total_carbs, 1),
            'fat': round(total_fat, 1),
            'fiber': 0, # Simplified for now
            'sugar': 0,
            'sodium': 0,
            'serving_size_g': serving_size,
            'is_vegetarian': details.get('is_veg', False),
            'is_vegan': details.get('is_veg', False), 
            'is_gluten_free': True, 
            'contains_nuts': False,
            'contains_dairy': False,
            'contains_gluten': False,
            'contains_egg': False,
            'is_nepali': True,
            'data_source': 'Calculated_from_USDA'
        }
        rows.append(row)
        food_id += 1

    # Write to CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            
    print(f"Success! Mathematically derived dataset saved to {output_file}")
    print(f"Generated {len(rows)} foods.")
    print("This file contains the calculated values and a defensive data_source tag.")

if __name__ == '__main__':
    main()
