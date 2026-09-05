# Deprecated / Quarantined Data Files

> **Audit Status:** Quarantined on September 5, 2026.

### Rationale:
The files in this directory (`raw_pasted_foods.json` and `clean_pasted_foods.json`) contained unverified web/LLM dumps with truncated responses, string IDs, duplicate dish names with conflicting calorie numbers, and equal-split ingredient estimation.

### Architectural Policy:
To preserve scientific rigor, academic defensibility, and clinical safety:
1. **Never import or cite these files in the production pipeline or thesis.**
2. All food items in `NepaliNutriDB` are verified against official references:
   - **USDA FoodData Central** (`https://fdc.nal.usda.gov/`)
   - **Nepal Government DFTQC Food Composition Tables**
   - **FAO / NARC Regional Food Composition Tables**
