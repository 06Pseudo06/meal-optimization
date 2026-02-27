"""
constraint_engine.py
Removes recipes that do not satisfy mandatory constraints.
"""

from typing import List, Dict
from app.ai.contracts.request_contract import RequestContract


def apply_constraints(
    recipes: List[Dict],
    request: RequestContract
) -> List[Dict]:
    
    if not recipes:
        return []

    filtered_recipes = []

    for recipe in recipes:

        # 1️⃣ Calorie Constraint
        if request.calorie_max is not None:
            if recipe.get("calories", 0) > request.calorie_max:
                continue

        # 2️⃣ Protein Constraint
        if request.protein_min is not None:
            if recipe.get("protein", 0) < request.protein_min:
                continue

        # 3️⃣ Diet Type Constraint
        if request.diet_type is not None:
            if recipe.get("diet_type") != request.diet_type:
                continue

        # 4️⃣ Ingredient Constraint
        if request.ingredients:
            recipe_ingredients = {
                i.lower() for i in recipe.get("ingredients", [])
            }
            required = {i.lower() for i in request.ingredients}

            if not required.issubset(recipe_ingredients):
                continue

        # 5️⃣ Goal Constraint
        if request.goal:
            if request.goal.lower() not in recipe.get("tags", "").lower():
                continue

        # 6️⃣ Mood Constraint
        if request.mood:
            if request.mood.lower() not in recipe.get("tags", "").lower():
                continue

        # 7️⃣ Time of Day Constraint
        if request.time_of_day:
            if request.time_of_day.lower() not in recipe.get("tags", "").lower():
                continue

        filtered_recipes.append(recipe)

    return filtered_recipes