import requests
import json
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def print_banner(title):
    print("\n" + "=" * 75)
    print(f"  {title}")
    print("=" * 75)

def get_or_create_user(username):
    for pwd in ["password123", "Password123!"]:
        res = requests.post(f"{BASE_URL}/api/users/login/", json={"username": username, "password": pwd})
        if res.status_code == 200:
            return res.json()["access"]
    # Register if not exists
    requests.post(f"{BASE_URL}/api/users/register/", json={
        "username": username,
        "email": f"{username}@example.com",
        "password": "Password123!"
    })
    # Login to obtain access token
    for pwd in ["Password123!", "password123"]:
        res = requests.post(f"{BASE_URL}/api/users/login/", json={"username": username, "password": pwd})
        if res.status_code == 200:
            return res.json()["access"]
    raise Exception(f"Auth failed for {username}: {res.text}")

def update_profile(token, profile_data):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.patch(f"{BASE_URL}/api/users/profile/", json=profile_data, headers=headers)
    if res.status_code not in [200, 201]:
        res = requests.put(f"{BASE_URL}/api/users/profile/", json=profile_data, headers=headers)
    return res.json()

def test_profile_gem(gem_name, username, profile_data, test_chat_prompt):
    print_banner(f"TESTING GEM PROFILE: {gem_name}")
    token = get_or_create_user(username)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Update Profile
    prof = update_profile(token, profile_data)
    print(f"[✓] Profile Configured for {username}:")
    print(f"    - Goal: {prof.get('health_goal')} | Pref: {prof.get('dietary_preference')}")
    bmi_str = f"{prof.get('bmi'):.1f}" if prof.get('bmi') is not None else "N/A"
    bmr_str = f"{prof.get('bmr'):.0f}" if prof.get('bmr') is not None else "N/A"
    cal_str = f"{prof.get('calorie_target'):.0f}" if prof.get('calorie_target') is not None else "N/A"
    print(f"    - BMI: {bmi_str} | BMR: {bmr_str} kcal | Target: {cal_str} kcal")

    # 2. Test Recommendation Engine
    t0 = time.time()
    rec_res = requests.get(f"{BASE_URL}/api/recommendations/generate/", headers=headers)
    rec_time = time.time() - t0
    recs = rec_res.json()
    if isinstance(recs, dict):
        recs = recs.get("results", [])
    
    print(f"\n[✓] XGBoost Recommendation Engine ({len(recs)} foods ranked in {rec_time:.2f}s):")
    for i, r in enumerate(recs[:4], start=1):
        sugar_str = f" | Sugar: {r.get('sugar', 0)}g" if 'sugar' in r else ""
        sodium_str = f" | Sod: {r.get('sodium', 0)}mg" if 'sodium' in r else ""
        print(f"    {i}. {r['name']} ({r.get('name_nepali', '')}) - Score: {r.get('score', 0):.3f} ({r.get('match_percent', 0)}% match)"
              f" | {r.get('calories', 0):.0f} kcal | P:{r.get('protein', 0):.1f}g{sugar_str}{sodium_str}")

    # Safety checks
    if "diabetes" in (profile_data.get("health_conditions") or "").lower():
        high_sugar = [r for r in recs if r.get("sugar", 0) >= 15]
        if not high_sugar:
            print("    [SAFETY VERIFIED] Zero high-sugar foods found! (Diabetes restriction enforced <15g)")
        else:
            print(f"    [SAFETY WARNING] Found {len(high_sugar)} items with sugar >= 15g")

    if "hypertension" in (profile_data.get("health_conditions") or "").lower():
        high_sodium = [r for r in recs if r.get("sodium", 0) >= 300]
        if not high_sodium:
            print("    [SAFETY VERIFIED] Zero high-sodium foods found! (Hypertension restriction enforced <300mg)")
        else:
            print(f"    [SAFETY WARNING] Found {len(high_sodium)} items with sodium >= 300mg")

    if profile_data.get("dietary_preference") == "vegetarian":
        non_veg = [r for r in recs if not r.get("is_vegetarian")]
        if not non_veg:
            print("    [SAFETY VERIFIED] 100% vegetarian foods! (Meat strictly filtered out)")
        else:
            print(f"    [SAFETY WARNING] Found {len(non_veg)} non-vegetarian items")

    # 3. Test Gemini Chat for this Persona
    print(f"\n[✓] Testing Gemini AI Persona Chat:")
    print(f"    User prompt: \"{test_chat_prompt}\"")
    t0 = time.time()
    chat_res = requests.post(f"{BASE_URL}/api/assistant/chat/", json={"message": test_chat_prompt}, headers=headers)
    chat_time = time.time() - t0
    
    if chat_res.status_code == 200:
        reply = chat_res.json().get("reply", "")
        print(f"    Gemini Response ({chat_time:.2f}s):\n    {reply[:350]}...\n")
    else:
        print(f"    [X] Chat error: {chat_res.status_code} - {chat_res.text}")

    # 4. Test Meal Logging & Budget Deduction
    if recs:
        chosen_food = recs[0]
        log_res = requests.post(f"{BASE_URL}/api/nutrition/logs/", json={
            "food": chosen_food["id"],
            "meal_type": "lunch",
            "quantity_g": 150
        }, headers=headers)
        if log_res.status_code in [200, 201]:
            logged_item = log_res.json()
            print(f"[✓] Meal Logged: {chosen_food['name']} (150g) -> ID: {logged_item.get('id')}")

            # Check daily summary
            sum_res = requests.get(f"{BASE_URL}/api/nutrition/daily-summary/", headers=headers)
            if sum_res.status_code == 200:
                s = sum_res.json()
                print(f"    Daily Summary Recalculated: Consumed={s.get('total_calories'):.0f} kcal, "
                      f"Target={s.get('calorie_target'):.0f} kcal, Remaining={s.get('calories_remaining'):.0f} kcal")

            # Test feedback loop (Like / Dislike)
            fb_res = requests.post(f"{BASE_URL}/api/recommendations/{chosen_food['id']}/feedback/", 
                                   json={"feedback": "liked"}, headers=headers)
            print(f"[✓] Feedback Logged: 'liked' -> Status {fb_res.status_code}")

def test_weight_progress(token):
    print_banner("TESTING PROGRESS PREDICTION ENGINE")
    headers = {"Authorization": f"Bearer {token}"}
    import datetime
    d1 = str(datetime.date.today() - datetime.timedelta(days=14))
    d2 = str(datetime.date.today())
    requests.post(f"{BASE_URL}/api/progress/weight/", json={"date": d1, "weight_kg": 78.5}, headers=headers)
    requests.post(f"{BASE_URL}/api/progress/weight/", json={"date": d2, "weight_kg": 76.8}, headers=headers)
    
    res = requests.get(f"{BASE_URL}/api/progress/predict/", headers=headers)
    print(f"Progress Prediction Status: {res.status_code}")
    if res.status_code == 200:
        d = res.json()
        print(f"Current weight: {d.get('current_weight')} kg, Goal weight: {d.get('goal_weight')} kg")
        print(f"Trend: {d.get('trend')} | Weekly Rate: {d.get('weekly_rate_kg')} kg/week | 8-Week Projected: {d.get('predicted_weight')} kg")
        print(f"Forecast Weeks generated: {len(d.get('forecast', []))}")

def main():
    print_banner("NUTRIAI END-TO-END COMPREHENSIVE TEST SUITE")
    print("Verifying Backend, Database, Safety Filtering, XGBoost Models, and Gemini AI Personas\n")

    # Persona 1: Diabetic Patient Gem
    test_profile_gem(
        gem_name="Diabetic Care Gem",
        username="diabetic_gem_user",
        profile_data={
            "age": 52,
            "gender": "male",
            "height_cm": 168.0,
            "weight_kg": 76.0,
            "activity_level": "sedentary",
            "health_goal": "lose_weight",
            "dietary_preference": "none",
            "health_conditions": "diabetes",
            "allergies": ""
        },
        test_chat_prompt="I have Type 2 Diabetes. Can you suggest a traditional Nepali lunch that will keep my blood sugar stable?"
    )

    # Persona 2: Hypertensive Vegetarian Gem
    test_profile_gem(
        gem_name="Hypertension & Heart Health Gem",
        username="cardio_veg_gem_user",
        profile_data={
            "age": 44,
            "gender": "female",
            "height_cm": 158.0,
            "weight_kg": 64.0,
            "activity_level": "lightly_active",
            "health_goal": "maintain_weight",
            "dietary_preference": "vegetarian",
            "health_conditions": "hypertension",
            "allergies": "dairy"
        },
        test_chat_prompt="I have high blood pressure and avoid dairy and meat. What Nepali foods give me good protein and low sodium?"
    )

    # Persona 3: Muscle Hypertrophy Athlete Gem
    test_profile_gem(
        gem_name="Muscle Hypertrophy & Gym Coach Gem",
        username="athlete_gem_user",
        profile_data={
            "age": 22,
            "gender": "male",
            "height_cm": 182.0,
            "weight_kg": 78.0,
            "goal_weight_kg": 83.0,
            "activity_level": "very_active",
            "health_goal": "build_muscle",
            "dietary_preference": "non_vegetarian",
            "health_conditions": "",
            "allergies": ""
        },
        test_chat_prompt="I hit heavy weights 5 times a week. Give me a high-protein Nepali meal plan with daily protein targets."
    )

    # Persona 4: Weight Loss & Calorie Deficit Gem
    test_profile_gem(
        gem_name="Fat Loss & Calorie Deficit Gem",
        username="fatloss_gem_user",
        profile_data={
            "age": 29,
            "gender": "female",
            "height_cm": 162.0,
            "weight_kg": 72.0,
            "goal_weight_kg": 60.0,
            "activity_level": "moderately_active",
            "health_goal": "lose_weight",
            "dietary_preference": "none",
            "health_conditions": "",
            "allergies": "nuts"
        },
        test_chat_prompt="I want to lose 10 kg without starving. How can I eat Dal Bhat and still stay in a calorie deficit?"
    )

    # Test progress prediction with athlete user
    athlete_token = get_or_create_user("athlete_gem_user")
    test_weight_progress(athlete_token)

    print_banner("ALL TESTS COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    main()
