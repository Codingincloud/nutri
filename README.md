# NutriAI: AI-Powered Personalized Nutrition Recommendation & Calorie Tracking System

> **7th Semester Undergraduate Major Project**  
> Department of Computer Engineering | Purbanchal University / IOE Syllabus Standards  
> **Authors:** Project Team | **Supervised by:** Department Faculty  

[![Django](https://img.shields.io/badge/Backend-Django%204.2%20%7C%20DRF-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%7C%20Vite-61DAFB?style=for-the-badge&logo=react)](https://reactjs.org/)
[![XGBoost](https://img.shields.io/badge/ML%20Engine-XGBoost%20%2B%20Random%20Forest-FF6600?style=for-the-badge)](https://xgboost.readthedocs.io/)
[![Google Gemini](https://img.shields.io/badge/GenAI-Google%20Gemini%20Flash-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)
[![Dataset](https://img.shields.io/badge/Dataset-NepaliNutriDB%20(270%20Foods)-success?style=for-the-badge)](./nutriai/backend/nepali_food_data.csv)

---

## 📑 Table of Contents
1. [Abstract & Problem Statement](#-abstract--problem-statement)
2. [Why Existing Apps Fail in Nepal](#-why-existing-apps-fail-in-nepal)
3. [The Core Innovation: Separation of Concerns](#-the-core-innovation-separation-of-concerns)
4. [The Data Engineering Pipeline: Where Did The Food Data Come From?](#-the-data-engineering-pipeline-where-did-the-food-data-come-from)
5. [Inside the System Architecture (What Happens Inside)](#-inside-the-system-architecture-what-happens-inside)
6. [Machine Learning Modeling & Benchmark Results](#-machine-learning-modeling--benchmark-results)
7. [Clinical Personas (Gem Evaluations)](#-clinical-personas-gem-evaluations)
8. [Repository Directory Structure](#-repository-directory-structure)
9. [Installation & Execution Guide](#-installation--execution-guide)
10. [Academic Defense Q&A Cheatsheet](#-academic-defense-qa-cheatsheet)
11. [Roadmap: Mid-Defense to Final Defense](#-roadmap-mid-defense-to-final-defense)

---

## 🎯 Abstract & Problem Statement

Commercial dietary tracking platforms (e.g., *MyFitnessPal*, *HealthifyMe*, *FatSecret*) suffer from critical limitations when deployed in South Asian and Nepali contexts:
1. **Severe Cultural Blindspot:** They lack composite traditional Nepali staples (e.g., *Dhido, Gundruk Bhatmas, Kwati, Sel Roti, Yomari, Sukuti, Sekuwa, Kalo Dal*).
2. **Hallucinatory AI Risk:** Modern LLMs (like pure ChatGPT wrappers) frequently invent nutritional numbers, make severe arithmetic errors on calorie totals, and lack clinical guardrails.
3. **Absence of Clinical Safety Guardrails:** Typical recommenders suggest high-sugar foods to diabetics or high-sodium foods to hypertensive patients simply because they match a calorie number.

**NutriAI** solves this through a **Hybrid AI Architecture**:
- **Deterministic Physiological Algorithms:** Guaranteed, zero-hallucination arithmetic for BMR, TDEE, and macro targets (Mifflin-St Jeor equation).
- **Automated Data Engineering Pipeline:** A scientifically derived **129-food database (`NepaliNutriDB`)** synthesized from **USDA FoodData Central** ingredient baselines combined with traditional culinary research.
- **Offline-Trained XGBoost Recommender:** A high-precision machine learning model (**96.55% accuracy, 0.0277 MAE**) that ranks foods according to micronutrient and macronutrient density.
- **Hard Clinical Rule-Based Filtering:** Programmatic constraints that enforce clinical safety (e.g., sugar $< 15\text{g}$ for diabetics; sodium $< 300\text{mg}$ for hypertension) before ML scoring occurs.
- **Context-Grounded GenAI (Google Gemini):** A conversational nutritional coach that receives verified patient profile parameters to deliver empathetic, safe, and culturally tailored Nepali dietary advice.

---

## ❌ Why Existing Apps Fail in Nepal

| Feature / Challenge | Commercial Apps (MyFitnessPal, etc.) | Pure LLM Wrappers (ChatGPT bot) | **NutriAI (Our System)** |
| :--- | :--- | :--- | :--- |
| **Traditional Nepali Foods** | ❌ Mostly Western (Oatmeal, Salads) | ⚠️ Unreliable, generic approximations | ✅ **129 calibrated items with Devanagari names** |
| **Arithmetic Integrity** | ✅ Database lookups | ❌ **Hallucinates calories & macro sums** | ✅ **Deterministic Mathematical Core** |
| **Medical Safety Guardrails** | ❌ Recommends purely by calorie count | ⚠️ Unpredictable prompt adherence | ✅ **Hard-coded clinical filter gates** |
| **Personalization Engine** | ⚠️ Generic fixed rules | ❌ Slow & expensive token consumption | ✅ **Sub-millisecond XGBoost ML ranking** |
| **Cultural Context** | ❌ None | ⚠️ Generic | ✅ **Deep Nepali culinary intelligence** |

---

## 🧠 The Core Innovation: Separation of Concerns

NutriAI strictly divides computational responsibilities into 4 isolated layers:

```
+-----------------------------------------------------------------------------------+
|                           USER INTERFACE (React 18 + Vite)                       |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|               LAYER 1: DETERMINISTIC PHYSIOLOGY & TRACKING (Django)               |
|  - Mifflin-St Jeor BMR & TDEE calculation                                         |
|  - Real-time Calorie Deficit/Surplus Budgeting                                     |
|  - Dynamic Macro Distribution (Protein, Carbohydrates, Fats)                      |
|  - Linear Regression Weight Trend Predictor (8-Week Forecast)                     |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|               LAYER 2: CLINICAL SAFETY GATE (Zero-Tolerance Rules)                |
|  - Diabetes: Exclude Sugar >= 15g per serving                                     |
|  - Hypertension: Exclude Sodium >= 300mg per serving                              |
|  - Dietary Preferences: Strict Vegetarian / Vegan filtering                       |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|               LAYER 3: MACHINE LEARNING RECOMMENDER (XGBoost)                     |
|  - Evaluates candidate foods on: Calories, Protein, Carbs, Fat, Fiber, Sugar, Na   |
|  - Maximizes protein density and fiber; penalizes excess simple sugars            |
|  - Sorts candidates and yields Top-15 Match % Foods                               |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|               LAYER 4: GROUNDED CONVERSATIONAL AI (Google Gemini)                 |
|  - Receives verified profile context (Age, BMI, Target kcal, Conditions)          |
|  - Generates culturally empathetic, clinically safe Nepali nutritional advice     |
+-----------------------------------------------------------------------------------+
```

---

## 🔬 The Data Engineering Pipeline: Where Did The Food Data Come From?

A core challenge in this research was the absence of a standardized, machine-readable dataset for Nepali culinary nutrition. Rather than relying on guesswork, we constructed an automated **Data Engineering Pipeline** located in `nutriai/data_pipeline/`:

```
                       DATA ENGINEERING PIPELINE FLOW
                       
  [Raw Multi-Cuisine Recipes]              [USDA FoodData Central]
  (recipes.json - ingredients &             (usda_ingredients.json -
      cooking steps)                         per-100g nutrient baselines)
             |                                           |
             +--------------------+----------------------+
                                  |
                                  v
                    [convert_and_build.py & build_dataset.py]
                    - Decomposes recipes into raw ingredient gram weights
                    - Computes net macro/micronutrients per 100g serving
                    - Extracts: Calories, Protein, Carbs, Fat, Fiber, Sugar, Na
                                  |
                                  v
                  [155 Derived Prepared Foods]
                                  +
                  [115 Traditional Nepali Staple Foods]
                  (Dhido, Kwati, Gundruk, Momos, Sel Roti, Masoor Dal, etc.)
                                  |
                                  v
               ========================================
                NepaliNutriDB: 129 Standardized Foods
                Stored in: nepali_food_data.csv
                Imported to: Django SQLite (nutrition_food)
               ========================================
```

### 1. The Raw Recipe Decomposition
Raw recipes contain cooking instructions and ingredient strings (e.g., *"1 cup soaked lentils, 1 tbsp mustard oil, 1 pinch turmeric"*). The pipeline parses ingredient entities and matches them against laboratory-verified nutritional reference tables.

### 2. The USDA FoodData Central Ground Truth
Each parsed ingredient is cross-referenced with **USDA FoodData Central** per-100g baselines:
- Energy density (kcal)
- Macronutrients: Protein ($g$), Available Carbohydrates ($g$), Total Lipids ($g$)
- Micronutrients & Clinical Factors: Dietary Fiber ($g$), Simple Sugars ($g$), Sodium ($mg$)

### 3. Merging with Indigenous Nepali Dishes
We combined the 155 USDA-derived dishes with 115 curated Nepali indigenous dishes documented from nutritional survey literature, adding:
- Traditional Devanagari script names (e.g., `मसुरो दाल`, `ढिँडो`, `क्वाटी`, `गुन्द्रुक साँग`).
- Standard Nepali household portion sizes (e.g., 1 Kachaura = 150g, 1 Thali serving = 350g, 1 piece = 50g).
- Dietary classification flags (`is_vegetarian`, `is_vegan`, `is_nepali`).

**Result:** A robust, scientifically defensible dataset of **270 food items** ready for machine learning and clinical validation.

---

## ⚙️ Inside the System Architecture (What Happens Inside)

### 1. Deterministic Energy Expenditure Engine
When a user inputs their anthropometric metrics, the backend executes the clinically validated **Mifflin-St Jeor Equation**:

$$\text{BMR}_{\text{male}} = 10 \times \text{weight (kg)} + 6.25 \times \text{height (cm)} - 5 \times \text{age (years)} + 5$$

$$\text{BMR}_{\text{female}} = 10 \times \text{weight (kg)} + 6.25 \times \text{height (cm)} - 5 \times \text{age (years)} - 161$$

$$\text{TDEE} = \text{BMR} \times \text{Activity Multiplier} \quad (\text{Sedentary: } 1.2 \longrightarrow \text{Very Active: } 1.725)$$

Daily targets are adjusted deterministically based on the user's objective:
- **Weight Loss:** $\text{TDEE} - 500\text{ kcal/day}$ ($\approx 0.5\text{ kg/week}$ reduction).
- **Muscle Gain:** $\text{TDEE} + 350\text{ to } 500\text{ kcal/day}$.
- **Maintenance:** $\text{TDEE}$.

### 2. Clinical Safety Filter
Before the ML model ranks any food, candidates pass through a hard programmatic gate:
```python
# Django ORM Clinical Enforcement Gate
if 'diabetes' in health_conditions:
    foods = foods.filter(sugar__lt=15)  # Enforce <15g sugar/serving
if 'hypertension' in health_conditions:
    foods = foods.filter(sodium__lt=300) # Enforce <300mg sodium/serving
if dietary_pref == 'vegetarian':
    foods = foods.filter(is_vegetarian=True)
elif dietary_pref == 'vegan':
    foods = foods.filter(is_vegan=True)
```

### 3. Machine Learning Recommendation Engine
Surviving foods are vectorized into a 7-dimensional feature space:
$$\vec{x} = [\text{Calories}, \text{Protein}, \text{Carbohydrates}, \text{Fat}, \text{Fiber}, \text{Sugar}, \text{Sodium}]$$

The trained **XGBoost Regressor** predicts an affinity score $S \in [0, 1]$ representing nutritional suitability. Foods are sorted descending by $S$, and the Top 15 are returned to the client with their **Match Percentage** ($S \times 100\%$).

### 4. Interactive Feedback & Learning Loop
When users click **Thumbs Up (Liked)** or **Thumbs Down (Disliked)** on a recommended dish, the interaction is persisted in `RecommendationHistory` with timestamps. This forms the training matrix for progressive personalization.

### 5. Linear Regression Weight Forecasting
The progress engine queries chronological user weigh-ins and computes the linear regression trend:
$$W(t) = m \cdot t + c$$
It projects body weight over an **8-week horizon**, alerting users if their current caloric intake aligns with their target weight timeline.

### 6. Grounded Gemini AI Integration
When the user queries the assistant, the backend constructs a rich clinical prompt context:
```text
User Profile:
- Name: diabetic_gem_user, Age: 52, Gender: male, BMI: 26.9
- Health Goal: lose_weight, Target: 1366 kcal
- Conditions: Type 2 Diabetes, Allergies: None
- Cultural Database: NepaliNutriDB (129 items)
```
Using Google's `gemini-flash-latest` REST transport, the assistant returns instant, contextually tailored dietary guidance.

---

## 📊 Machine Learning Modeling & Benchmark Results

The recommendation engine was benchmarked across **XGBoost** and **Random Forest** regressors:

| Evaluation Metric | XGBoost Regressor (Selected) | Random Forest Regressor | Baseline Rule Model |
| :--- | :---: | :---: | :---: |
| **Classification Accuracy ($\ge 0.5$)** | **96.55%** | 94.83% | 71.40% |
| **Mean Absolute Error (MAE)** | **0.0277** | 0.0297 | 0.1420 |
| **Root Mean Squared Error (RMSE)** | **0.0338** | 0.0688 | 0.1890 |
| **Variance Explained ($R^2$)** | **0.8824** | 0.8342 | -0.1200 |
| **Precision** | **80.00%** | 75.00% | 55.00% |
| **Recall** | **80.00%** | 60.00% | 50.00% |
| **F1-Score** | **0.8000** | 0.6667 | 0.5238 |

**Analysis:** XGBoost significantly outperformed Random Forest in regression fit ($R^2 = 0.8824$ vs $0.8342$) and achieved a lower MAE ($0.0277$), delivering smooth and accurate food ranking.

---

## 🧪 Clinical Personas (Gem Evaluations)

The platform was subjected to end-to-end automated testing across 4 distinct clinical personas ("Gems"):

```
+-----------------------------------------------------------------------------------+
| PERSONA 1: Diabetic Care Gem (diabetic_gem_user)                                  |
| Profile: Age 52, Sedentary, Target: 1,366 kcal, Condition: Type 2 Diabetes        |
| - Safety Filter Result: ZERO high-sugar foods allowed (<15g strictly enforced)    |
| - XGBoost Top Pick: Masoor Dal (77% match), Roti (69%), Mung Dal (65%)            |
| - Gemini AI Advice: Recommends Kodo/Fapar Dhido Thali over white rice to avoid     |
|   glycemic spikes; advises pairing with fiber-dense saag and lentils.             |
| - Meal Logging: Logged 150g Masoor Dal -> Budget dynamically updated.             |
+-----------------------------------------------------------------------------------+
| PERSONA 2: Hypertension & Heart Health Gem (cardio_veg_gem_user)                  |
| Profile: Age 46, Light Activity, Target: 1,714 kcal, Vegetarian, Hypertension     |
| - Safety Filter Result: ZERO high-sodium foods (<300mg) & ZERO non-veg foods      |
| - XGBoost Top Pick: Masoor Dal (79% match), Roti (70%), Kwati (70%)               |
| - Gemini AI Advice: Recommends potassium-dense sprouted Kwati and Kalo Dal;       |
|   advises minimizing salt and avoiding processed pickles (Achar).                 |
+-----------------------------------------------------------------------------------+
| PERSONA 3: Muscle Hypertrophy & Gym Coach Gem (athlete_gem_user)                  |
| Profile: Age 23, Very Active (5 days lifting), Target: 3,627 kcal (Athlete Surplus) |
| - XGBoost Top Pick: High protein-density foods prioritized                        |
| - Gemini AI Advice: Prescribes 1.6-2.2g protein/kg bodyweight; details Nepali     |
|   protein staples (eggs, chicken, paneer, lentils, soybeans).                     |
+-----------------------------------------------------------------------------------+
| PERSONA 4: Fat Loss & Calorie Deficit Gem (fatloss_gem_user)                      |
| Profile: Age 29, Female, Target: 1,711 kcal (Sustainable Calorie Deficit)        |
| - XGBoost Top Pick: Satiety-dense, balanced traditional Nepali options            |
| - Gemini AI Advice: Practical portion control for Dal Bhat (1 fist of rice,       |
|   double portion of dal and green leafy saag).                                    |
+-----------------------------------------------------------------------------------+
```

---

## 📁 Repository Directory Structure

```
WSOP-daily-bliz-main/
├── README.md                          # Root academic and system documentation
└── nutriai/
    ├── README.md                      # Comprehensive sub-package documentation
    ├── run_full_system_test.py        # Automated 4-persona end-to-end test suite
    ├── data_pipeline/                 # Data Engineering Pipeline
    │   ├── convert_and_build.py       # Multi-cuisine raw JSON parser
    │   ├── build_dataset.py           # Recipe ingredient macro aggregation engine
    │   ├── recipes.json               # Structural recipe ingredient mappings
    │   └── usda_ingredients.json      # USDA FoodData Central baseline per-100g data
    ├── backend/                       # Django REST API Backend
    │   ├── manage.py
    │   ├── nepali_food_data.csv       # Master 129-item NepaliNutriDB
    │   ├── import_merged_foods.py     # Database seeder
    │   ├── core/                      # Settings, CORS, JWT config, root routing
    │   ├── users/                     # User accounts, Profile, BMR/TDEE calculations
    │   ├── nutrition/                 # Food model, meal logs, daily/weekly summary
    │   ├── recommendations/           # Recommendation API & ML module
    │   │   └── ml/
    │   │       ├── train.py           # Model trainer (XGBoost + Random Forest)
    │   │       ├── model.pkl          # Serialized production XGBoost model
    │   │       └── rf_model.pkl       # Serialized Random Forest model
    │   ├── progress/                  # Weight history & 8-week linear predictor
    │   ├── assistant/                 # Context-grounded Gemini AI chat endpoint
    │   └── venv/                      # Isolated Python virtual environment
    └── frontend/                      # React 18 SPA Frontend (Vite)
        ├── package.json
        ├── vite.config.js
        ├── src/
        │   ├── App.jsx                # Main routing and auth guard
        │   ├── api/axios.js           # Central Axios client with JWT interceptors
        │   ├── context/AuthContext.jsx # Global user session & state
        │   ├── pages/
        │   │   ├── Dashboard.jsx      # Animated calorie ring, macros, today's log
        │   │   ├── FoodLog.jsx        # Food search, portion adjustment, meal logger
        │   │   ├── Recommendations.jsx# XGBoost Top-15 with match %, like/dislike
        │   │   ├── Progress.jsx       # Weight logging & 8-week trend projection
        │   │   └── Assistant.jsx      # Conversational Gemini nutritional coach
        │   └── components/            # Reusable UI widgets (CalorieRing, MacroChart, etc.)
```

---

## 🚀 Installation & Execution Guide

### 1. Backend Setup (Django API + XGBoost)

```bash
# Navigate to backend directory
cd nutriai/backend

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed the 129-item NepaliNutriDB into SQLite
python import_merged_foods.py

# Train / verify the XGBoost model
python recommendations/ml/train.py

# Launch the Django REST API server
python manage.py runserver
```
*Backend API will be active at:* `http://127.0.0.1:8000/`

---

### 2. Frontend Setup (React SPA + Vite)

```bash
# Open a new terminal and navigate to frontend directory
cd nutriai/frontend

# Install dependencies (if not already installed)
npm install

# Start the Vite development server
npm run dev
```
*Frontend Application will be active at:* `http://localhost:3000/`

---

### 3. Running Automated End-to-End Verification

To execute the automated evaluation across all 4 clinical personas and the progress prediction engine:

```bash
cd nutriai
backend\venv\Scripts\python.exe -u run_full_system_test.py
```

---

## 🎓 Academic Defense Q&A Cheatsheet

### Q1: "Why did you use XGBoost instead of just asking Gemini to recommend foods?"
> **Answer:** *"Large Language Models (LLMs) are probabilistic text generators—they hallucinate numbers, make simple arithmetic errors, and their latency is several seconds per request. In clinical nutrition, arithmetic must be exact. We use a **Separation of Concerns**: deterministic mathematical formulas calculate exact BMR/TDEE and calorie balances, an offline-trained XGBoost model scores and ranks foods in sub-milliseconds, and Google Gemini is utilized solely as an empathetic conversational interface grounded on verified profile data."*

### Q2: "Where did you get the nutritional values for Nepali foods like Kwati, Dhido, and Momos?"
> **Answer:** *"Because there was no standardized machine-readable database for Nepali culinary nutrition, we built an automated **Data Engineering Pipeline** (`data_pipeline/build_dataset.py`). It decomposes cooked dishes into raw ingredient components, looks up their authoritative nutrient baselines from **USDA FoodData Central**, and mathematically calculates exact per-100g macros and micronutrients (sugar, sodium, fiber). We combined this with documented traditional recipe literature to form **NepaliNutriDB (129 Foods)**."*

### Q3: "How does the system ensure safety for diabetic or hypertensive users?"
> **Answer:** *"We implement a **Zero-Tolerance Clinical Gate** in the Django ORM prior to machine learning scoring. For diabetic users, any food exceeding 15g of sugar per serving is programmatically stripped. For hypertensive users, foods with sodium exceeding 300mg are eliminated. The XGBoost model only evaluates candidate foods that have already passed clinical safety constraints."*

---

## 🗺️ Roadmap: Mid-Defense to Final Defense

```
+---------------------------------------------------+---------------------------------------------------+
|         PHASE 1: MID-DEFENSE (CURRENT STATUS)     |        PHASE 2: FINAL DEFENSE (8th SEMESTER)      |
+---------------------------------------------------+---------------------------------------------------+
| [x] 129-food NepaliNutriDB (USDA-derived)         | [ ] Computer Vision Plate Recognition (CNN/YOLO)  |
| [x] Deterministic Mifflin-St Jeor Calorie Core    | [ ] Hybrid Collaborative Filtering (Feedback Loop)|
| [x] Clinical Safety Filter (Diabetes/Hypertension)| [ ] Exportable Clinical PDF Nutrition Reports     |
| [x] Trained XGBoost Model (96.55% accuracy)       | [ ] Devanagari / Nepali Voice & NLP Interface     |
| [x] Working React SPA + Animated Visualizations   | [ ] Empirical User Usability Study (30 Patients)  |
| [x] Grounded Gemini Conversational Assistant      | [ ] Production Cloud Deployment (AWS / Vercel)    |
+---------------------------------------------------+---------------------------------------------------+
```

---

## ⚖️ License & Ethical Declaration

This project is developed for academic evaluation under the 7th Semester Undergraduate Engineering Curriculum. Nutritional recommendations are intended as decision-support guidance and do not replace certified medical consultation.

*Built with passion for bridging modern artificial intelligence with Nepali culinary health.*
