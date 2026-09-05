import csv
import os

def main():
    backend_data_dir = '../backend/data'
    derived_csv = os.path.join(backend_data_dir, 'nepali_foods_derived.csv')
    existing_csv = os.path.join(backend_data_dir, 'nepali_food_data.csv')
    
    existing_foods = {}
    fieldnames = []
    
    if os.path.exists(existing_csv):
        with open(existing_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                existing_foods[row['name'].strip().lower()] = row

    if os.path.exists(derived_csv):
        with open(derived_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not fieldnames:
                fieldnames = reader.fieldnames
            for row in reader:
                name_key = row['name'].strip().lower()
                if name_key not in existing_foods:
                    existing_foods[name_key] = row
                else:
                    # Update source and macros to derived
                    existing_foods[name_key]['data_source'] = 'Calculated_from_USDA'
                    existing_foods[name_key]['calories'] = row['calories']
                    existing_foods[name_key]['protein'] = row['protein']
                    existing_foods[name_key]['carbohydrates'] = row['carbohydrates']
                    existing_foods[name_key]['fat'] = row['fat']

    # Assign clean food_ids
    merged_rows = list(existing_foods.values())
    for idx, row in enumerate(merged_rows, start=1):
        row['food_id'] = idx

    # Save to existing_csv (nepali_food_data.csv)
    with open(existing_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in merged_rows:
            writer.writerow(row)

    print(f"Successfully merged datasets into {existing_csv}.")
    print(f"Total foods in dataset: {len(merged_rows)}")

if __name__ == '__main__':
    main()
