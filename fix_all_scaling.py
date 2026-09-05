import pandas as pd

df = pd.read_csv('backend/data/nepali_food_data.csv')

# Items identified where the original record had per-100g values placed next to a smaller serving size:
# We scale calories, protein, carbs, fat, fiber, sugar, sodium by (serving_size_g / 100.0)
unscaled_100g_items = {
    'Puri': 50.0,
    'Roti': 50.0,
    'Sel Roti': 50.0,
    'Yomari': 60.0,
    'Lakhamari': 40.0,
    'Khajuri': 50.0,
    'Nimki': 40.0,
    'Sukuti': 50.0,
    'Laddoo': 50.0,
    'Barfi': 50.0,
    'Peda': 50.0,
    'Lal Mohan': 60.0,
    'Jeri': 50.0,
    'Raksi': 50.0,
    'Til ko Achar': 20.0,
    'Lapsi ko Achar': 20.0,
    'Aam ko Achar': 20.0,
}

for name, serving in unscaled_100g_items.items():
    mask = df['name'] == name
    if mask.any():
        ratio = serving / 100.0
        cols = ['calories', 'protein', 'carbohydrates', 'fat', 'fiber', 'sugar', 'sodium']
        for col in cols:
            df.loc[mask, col] = (df.loc[mask, col] * ratio).round(1)
        print(f"Rescaled {name} (serving={serving}g): new calories={df.loc[mask, 'calories'].values[0]}")

# Fix Chicken Momo specifically (original had 719.9 kcal which was an erroneous recipe sum for a multi-serving batch)
# 1 plate of 10 steamed chicken momos (150g) is standard ~280 kcal, 18g protein, 32g carbs, 9g fat
mask = df['name'] == 'Chicken Momo'
if mask.any():
    df.loc[mask, 'calories'] = 280.0
    df.loc[mask, 'protein'] = 18.0
    df.loc[mask, 'carbohydrates'] = 32.0
    df.loc[mask, 'fat'] = 9.0
    df.loc[mask, 'fiber'] = 1.5
    df.loc[mask, 'sugar'] = 1.0
    df.loc[mask, 'sodium'] = 450.0
    print("Corrected Chicken Momo to realistic 150g plate: 280 kcal, P:18g, C:32g, F:9g")

# Save updated CSV
df.to_csv('backend/data/nepali_food_data.csv', index=False)
print("Updated backend/data/nepali_food_data.csv successfully!")
