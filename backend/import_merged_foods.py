import os
import sys
import csv
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from nutrition.models import Food

def str2bool(val):
    return str(val).strip().lower() in ['true', '1', 't', 'yes']

def float2val(val, default=0.0):
    try:
        return float(val)
    except:
        return default

def main():
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'nepali_food_data.csv')
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        updated = 0
        for row in reader:
            name = row.get('name', '').strip()
            if not name:
                continue
            
            category = row.get('category', 'nepali_staple').strip()
            # fallback category if not in choices
            valid_categories = [c[0] for c in Food.CATEGORY_CHOICES]
            if category not in valid_categories:
                category = 'snack' if 'snack' in category else ('international' if 'dish' in category or 'global' in category else 'nepali_staple')

            food, created = Food.objects.update_or_create(
                name=name,
                defaults={
                    'name_nepali': row.get('name_nepali', ''),
                    'category': category,
                    'calories': float2val(row.get('calories')),
                    'protein': float2val(row.get('protein')),
                    'carbohydrates': float2val(row.get('carbohydrates')),
                    'fat': float2val(row.get('fat')),
                    'fiber': float2val(row.get('fiber')),
                    'sugar': float2val(row.get('sugar')),
                    'sodium': float2val(row.get('sodium')),
                    'serving_size_g': float2val(row.get('serving_size_g'), 100.0),
                    'is_vegetarian': str2bool(row.get('is_vegetarian')),
                    'is_vegan': str2bool(row.get('is_vegan')),
                    'is_gluten_free': str2bool(row.get('is_gluten_free')),
                    'contains_nuts': str2bool(row.get('contains_nuts')),
                    'contains_dairy': str2bool(row.get('contains_dairy')),
                    'contains_gluten': str2bool(row.get('contains_gluten')),
                    'contains_egg': str2bool(row.get('contains_egg')),
                    'is_nepali': str2bool(row.get('is_nepali')),
                    'data_source': row.get('data_source', 'Calculated_from_USDA')
                }
            )
            if created:
                count += 1
            else:
                updated += 1

    # Remove old/orphaned junk foods not in the clean dataset
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        valid_names = set(r['name'].strip() for r in reader if r.get('name'))
    
    deleted_count, _ = Food.objects.exclude(name__in=valid_names).delete()
    if deleted_count > 0:
        print(f"Purged {deleted_count} outdated/filler food items from database.")

    print(f"Import complete! Created {count} new foods, updated {updated} existing foods.")
    print(f"Total verified foods in DB: {Food.objects.count()}")

if __name__ == '__main__':
    main()
