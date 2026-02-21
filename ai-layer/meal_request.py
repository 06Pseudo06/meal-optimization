import json

# ===== TAKE MEAL REQUEST INPUT =====

meal_type = input("Enter meal type (breakfast/lunch/dinner): ")
goal_context = input("Enter goal context (e.g., muscle_recovery): ")

calorie_min = int(input("Enter minimum calories: "))
calorie_max = int(input("Enter maximum calories: "))

protein_min = int(input("Enter minimum protein (g): "))
carbs_max = int(input("Enter maximum carbs (g): "))
fat_max = int(input("Enter maximum fat (g): "))
fibre_min = int(input("Enter minimum fibre (g): "))

required_input = input("Enter required ingredients (comma separated): ")
required_ingredients = [r.strip() for r in required_input.split(",")] if required_input else []

excluded_input = input("Enter excluded ingredients (comma separated): ")
excluded_ingredients = [e.strip() for e in excluded_input.split(",")] if excluded_input else []

macro_priority = input("Enter macro priority (e.g., high_protein): ")

# ===== BUILD JSON STRUCTURE =====

meal_request_data = {
    "meal_request": {
        "meal_type": meal_type,
        "goal_context": goal_context,
        "calorie_constraint": {
            "min": calorie_min,
            "max": calorie_max
        },
        "macro_constraints": {
            "protein_min_g": protein_min,
            "carbs_max_g": carbs_max,
            "fat_max_g": fat_max,
            "fibre_min_g": fibre_min
        },
        "ingredient_constraints": {
            "required": required_ingredients,
            "excluded": excluded_ingredients
        },
        "macro_priority": macro_priority
    }
}

# ===== WRITE TO JSON FILE =====

with open("meal_request.json", "w") as f:
    json.dump(meal_request_data, f, indent=4)

print("\nMeal request saved successfully.\n")
print(json.dumps(meal_request_data, indent=4))
