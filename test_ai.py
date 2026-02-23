from AI.engine import generate_recommendations

mock_user = {}

mock_request = {
    "calorie_max": 600,
    "protein_min": 20,
    "diet_type": "veg",
    "ingredients": ["rice"],
    "goal": None,
    "mood": None,
    "time_of_day": None,
}

mock_recipes = [
    {
        "id": 1,
        "name": "Veg Rice Bowl",
        "calories": 500,
        "protein": 25,
        "carbs": 60,
        "fats": 10,
        "diet_type": "veg",
        "ingredients": ["rice", "beans"],
        "tags": "lunch"
    },
    {
        "id": 2,
        "name": "Chicken Plate",
        "calories": 700,
        "protein": 40,
        "carbs": 50,
        "fats": 20,
        "diet_type": "non-veg",
        "ingredients": ["chicken", "rice"],
        "tags": "dinner"
    }
]

results = generate_recommendations(
    user=mock_user,
    recipes=mock_recipes,
    request=mock_request
)

print(results)