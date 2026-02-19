import json

print("Program started")

food_id = input("Enter Food ID: ")
name = input("Enter Food Name: ")

calories = int(input("Enter calories: "))
protein = int(input("Enter protein (g): "))
carbs = int(input("Enter carbs (g): "))
fat = int(input("Enter fat (g): "))
fibre = int(input("Enter fibre (g): "))

food_item = {
    "id": food_id,
    "name": name,
    "nutrition_per_serving": {
        "calories": calories,
        "protein_g": protein,
        "carbs_g": carbs,
        "fat_g": fat,
        "fibre_g": fibre
    }
}

with open("food_schema.json", "w") as f:
    json.dump(food_item, f, indent=4)

print("Saved successfully.")
print(json.dumps(food_item, indent=4))
