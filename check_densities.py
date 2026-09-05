import pandas as pd

df = pd.read_csv('backend/data/nepali_food_data.csv')
print("Foods with calorie density > 4.5 kcal/g (suspect unrescaled):")
for i, r in df.iterrows():
    cal_density = r['calories'] / r['serving_size_g']
    if cal_density > 4.5:
        print(f"  ID {r['food_id']:3d}: {r['name']:25s} | serv={r['serving_size_g']}g | cal={r['calories']} | density={cal_density:.2f} kcal/g")
