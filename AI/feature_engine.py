"""
feature_engine.py
Converts recipe + request into normalized numeric signals (0–1).
"""

from typing import Dict
from AI.contracts.recipe_contract import RecipeContract
from AI.contracts.request_contract import RequestContract


def compute_features(
    recipe: RecipeContract,
    request: RequestContract
) -> Dict[str, float]:

    features: Dict[str, float] = {}

    # ----------------------------
    # 1️⃣ Ingredient Match (Soft Ratio)
    # ----------------------------
    if request.ingredients:
        user_set = {i.lower() for i in request.ingredients}
        recipe_set = {i.lower() for i in (recipe.ingredients or [])}

        if user_set:
            matches = len(recipe_set.intersection(user_set))
            features["ingredient_match"] = matches / len(user_set)
        else:
            features["ingredient_match"] = 0.0
    else:
        features["ingredient_match"] = 0.0

    # ----------------------------
    # 2️⃣ Protein Alignment
    # ----------------------------
    if request.protein_min:
        features["protein_alignment"] = min(
            recipe.protein / request.protein_min,
            1.0
        )
    else:
        # Normalize against upper bound (100g assumption)
        features["protein_alignment"] = min(
            recipe.protein / 100,
            1.0
        )

    # ----------------------------
    # 3️⃣ Calorie Alignment
    # ----------------------------
    if request.calorie_max:
        alignment = 1 - (recipe.calories / request.calorie_max)
        features["calorie_alignment"] = max(alignment, 0.0)
    else:
        features["calorie_alignment"] = 1.0

    # ----------------------------
    # 4️⃣ Goal Tag Match
    # ----------------------------
    if request.goal and recipe.tags:
        features["goal_tag_match"] = (
            1.0 if request.goal.lower() in recipe.tags.lower()
            else 0.0
        )
    else:
        features["goal_tag_match"] = 0.0

    # ----------------------------
    # 5️⃣ Macro Density (Protein Efficiency)
    # ----------------------------
    if recipe.calories > 0:
        density = recipe.protein / recipe.calories
        features["macro_density"] = min(density / 0.3, 1.0)
    else:
        features["macro_density"] = 0.0

    return features