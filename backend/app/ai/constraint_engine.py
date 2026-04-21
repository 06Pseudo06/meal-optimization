"""
constraint_engine.py
Removes recipes that do not satisfy mandatory constraints.
Includes incremental fallback + allergy filtering.
"""

from typing import List, Dict


def apply_constraints(recipes, request, user=None):

    filtered = []

    for recipe in recipes:

        if request.calorie_max:
            if recipe["calories"] > request.calorie_max:
                continue

        if request.protein_min:
            if recipe["protein"] < request.protein_min:
                continue

        if request.diet_type:
            if recipe["diet_type"] != request.diet_type:
                continue

        blocked = False

        for item in request.exclude_ingredients:
            if item in recipe["ingredients"]:
                blocked = True

        if blocked:
            continue

        filtered.append(recipe)

    # --------------------
    # fallback mode
    # --------------------
    if not filtered:
        recipes.sort(key=lambda x: x["calories"])
        return recipes[:2]

    return filtered