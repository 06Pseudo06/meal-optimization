"""
feature_engine.py
Converts recipe + request + user profile
into normalized numeric signals (0–1).
"""

from pyexpat import features
from typing import Dict
from app.ai.contracts.recipe_contract import RecipeContract
from app.ai.contracts.user_contract import UserContract
from app.ai.contracts.request_contract import RequestContract


def compute_features(
    recipe: RecipeContract,
    request: RequestContract,
    user: UserContract
) -> Dict[str, float]:

    features: Dict[str, float] = {}

    # --------------------------------------------------
    # 1️⃣ Ingredient Match (Soft Ratio)
    # --------------------------------------------------
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

    # --------------------------------------------------
    # 2️⃣ Protein Alignment (Personalized)
    # --------------------------------------------------
    target_protein = user.daily_protein_target

    if target_protein and target_protein > 0:
        # Align to user's daily protein goal
        protein_alignment = recipe.protein / target_protein
        protein_alignment = max(0.0, min(protein_alignment, 1.0))
        features["protein_alignment"] = protein_alignment

    elif request.protein_min:
        # Fallback to request constraint
        features["protein_alignment"] = min(
            recipe.protein / request.protein_min,
            1.0
        )
    else:
        # Generic normalization fallback
        features["protein_alignment"] = min(
            recipe.protein / 100,
            1.0
        )

    # --------------------------------------------------
    # 3️⃣ Calorie Alignment (Personalized)
    # --------------------------------------------------
    target_calories = user.daily_calorie_target

    if target_calories and target_calories > 0:
        calorie_deviation = abs(recipe.calories - target_calories)
        calorie_alignment = 1 - (calorie_deviation / target_calories)
        calorie_alignment = max(0.0, min(calorie_alignment, 1.0))
        features["calorie_alignment"] = calorie_alignment

    elif request.calorie_max:
        alignment = 1 - (recipe.calories / request.calorie_max)
        features["calorie_alignment"] = max(alignment, 0.0)
    else:
        features["calorie_alignment"] = 1.0

    # --------------------------------------------------
    # 4️⃣ Goal Tag Match
    # --------------------------------------------------
    if request.goal and recipe.tags:
        features["goal_tag_match"] = (
            1.0 if request.goal.lower() in recipe.tags.lower()
            else 0.0
        )
    else:
        features["goal_tag_match"] = 0.0

    # --------------------------------------------------
    # 5️⃣ Macro Density (Protein Efficiency)
    # --------------------------------------------------
    if recipe.calories > 0:
        density = recipe.protein / recipe.calories
        features["macro_density"] = min(density / 0.3, 1.0)
    else:
        features["macro_density"] = 0.0

    # --------------------------------------------------
    # 6️⃣ Carb Ratio
    # --------------------------------------------------
    if recipe.carbs is not None and recipe.carbs > 0:
        carb_ratio = recipe.carbs / 300   # avg daily carbs
        features["carb_ratio"] = min(carb_ratio, 1.0)
    else:
        features["carb_ratio"] = 0.0


    # --------------------------------------------------
    # 7️⃣ Fat Ratio
    # --------------------------------------------------
    if recipe.fats is not None and recipe.fats > 0:
        fat_ratio = recipe.fats / 70   # avg daily fats
        features["fat_ratio"] = min(fat_ratio, 1.0)
    else:
        features["fat_ratio"] = 0.0

    return features