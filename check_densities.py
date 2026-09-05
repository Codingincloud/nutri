import pandas as pd

df = pd.read_csv('backend/data/nepali_food_data.csv')
print("Foods with calorie density > 4.5 kcal/g (suspect unrescaled cooked foods):")
# Note: Pure dietary fats (Oils, Ghee) are physically ~8.8 - 9.0 kcal/g.
# Raw tree nuts (peanuts, walnuts) are naturally ~5.5 - 6.6 kcal/g.
# This check isolates cooked composite dishes or snacks that should NOT exceed 4.5 kcal/g.
for i, r in df.iterrows():
    cal_density = r['calories'] / r['serving_size_g']
    cat = str(r.get('category', ''))
    is_pure_lipid = cat in ['fat_oil', 'fat'] or 'oil' in r['name'].lower() or 'ghee' in r['name'].lower()
    is_raw_nut = 'walnut' in r['name'].lower() or 'peanut' in r['name'].lower() or 'badam' in r['name'].lower()
    
    if cal_density > 4.5:
        lipid_tag = " [Natural Pure Fat/Oil]" if is_pure_lipid else (" [Natural Tree Nut]" if is_raw_nut else " [ALERT: SUSPECT COOKED DISH]")
        print(f"  ID {r['food_id']:3d}: {r['name']:25s} | serv={r['serving_size_g']}g | cal={r['calories']} | density={cal_density:.2f} kcal/g{lipid_tag}")

