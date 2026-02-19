import json

# Take user input
user_id = input("Enter User ID: ")
age = int(input("Enter age: "))
gender = input("Enter gender: ")
weight = float(input("Enter weight (kg): "))
height = float(input("Enter height (cm): "))
activity_level = input("Enter activity level: ")
fitness_goal = input("Enter fitness goal: ")
diet_type = input("Enter diet type: ")
daily_budget = float(input("Enter daily budget: "))

# Build JSON structure
user_profile = {
    "user_id": user_id,
    "personal_info": {
        "age": age,
        "gender": gender,
        "weight_kg": weight,
        "height_cm": height,
        "activity_level": activity_level
    },
    "fitness_goals": fitness_goal,
    "dietary_preferences": {
        "diet_type": diet_type,
        "allergies": [],
        "excluded_ingredients": []
    },
    "budget": {
        "daily_limit": daily_budget
    }
}

# Write to JSON file
with open("user_profile.json", "w") as f:
    json.dump(user_profile, f, indent=4)

print("Data saved to user_profile.json successfully.")
