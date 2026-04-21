from app.ai.engine import generate_recommendations

# Dummy user
user = {
    "id": 1,
    "daily_calorie_target": 2000,
    "daily_protein_target": 100,
    "allergies": ["Paneer"]
}

# Dummy recipes
recipes = [
    {
        "id": 1,
        "name": "Egg Curry",
        "calories": 400,
        "protein": 30,
        "diet_type": "veg",
        "ingredients": ["egg"],
        "tags": "high protein"
    },
    {
        "id": 2,
        "name": "Paneer Salad",
        "calories": 300,
        "protein": 20,
        "diet_type": "veg",
        "ingredients": ["paneer"],
        "tags": "light"
    }
]

# Dummy request
request = {
    "calorie_max": 500,
    "protein_min": 20,
    "diet_type": "veg"
}

# Run engine
result = generate_recommendations(user, recipes, request)

# Print result
import json
print(json.dumps(result, indent=2))