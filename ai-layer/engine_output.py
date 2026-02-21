import json

# ===== TAKE INPUT =====

meal_type = input("Enter meal type: ")
food_id = input("Enter food ID: ")
food_name = input("Enter food name: ")
servings = int(input("Enter number of servings: "))

calories_per_serving = int(input("Enter calories per serving: "))
protein_per_serving = int(input("Enter protein per serving (g): "))
carbs_per_serving = int(input("Enter carbs per serving (g): "))
fat_per_serving = int(input("Enter fat per serving (g): "))
cost_per_serving = int(input("Enter cost per serving: "))

# ===== CALCULATE TOTALS =====

total_calories = calories_per_serving * servings
total_protein = protein_per_serving * servings
total_carbs = carbs_per_serving * servings
total_fat = fat_per_serving * servings
total_cost = cost_per_serving * servings

# ===== BUILD ENGINE OUTPUT =====

engine_output = {
    "meal_type": meal_type,
    "selected_meals": [
        {
            "food_id": food_id,
            "name": food_name,
            "servings": servings
        }
    ],
    "total_nutrition": {
        "calories": total_calories,
        "protein_g": total_protein,
        "carbs_g": total_carbs,
        "fats_g": total_fat
    },
    "cost_total": total_cost,
    "score": 0.89,
    "explanation_summary": "High protein alignment for muscle recovery within calorie constraint."
}

# ===== SAVE TO FILE =====

with open("engine_output.json", "w") as f:
    json.dump(engine_output, f, indent=4)

print("\nEngine output generated:\n")
print(json.dumps(engine_output, indent=4))
