from typing import Dict, Set


def compute_features(recipe, request, recipe_ingredients: Set[str]) -> Dict[str, float]:
    """
    Compute normalized feature signals for ranking.
    All features are scaled between 0 and 1 where possible.
    """

    features: Dict[str, float] = {}

    # --------------------------------------------------
    # 1️⃣ Ingredient Match Ratio
    # --------------------------------------------------
    if request.ingredients:
        user_set = {ingredient.lower() for ingredient in request.ingredients}

        if user_set:
            matches = len(recipe_ingredients.intersection(user_set))
            features["ingredient_match"] = matches / len(user_set)
        else:
            features["ingredient_match"] = 0.0
    else:
        features["ingredient_match"] = 0.0


    # --------------------------------------------------
    # 2️⃣ Protein Alignment
    # --------------------------------------------------
    if request.protein_min:
        # If protein >= required → full score (1)
        features["protein_alignment"] = min(
            recipe.protein / request.protein_min, 1.0
        )
    else:
        # Normalize against reasonable upper bound (e.g., 100g)
        features["protein_alignment"] = min(recipe.protein / 100, 1.0)


    # --------------------------------------------------
    # 3️⃣ Calorie Alignment (inverse penalty)
    # --------------------------------------------------
    if request.calorie_max:
        if request.calorie_max > 0:
            alignment = 1 - (recipe.calories / request.calorie_max)
            features["calorie_alignment"] = max(alignment, 0.0)
        else:
            features["calorie_alignment"] = 0.0
    else:
        features["calorie_alignment"] = 1.0


    # --------------------------------------------------
    # 4️⃣ Goal Tag Match
    # --------------------------------------------------
    if request.goal and recipe.tags:
        features["goal_tag_match"] = (
            1.0 if request.goal.lower() in recipe.tags.lower() else 0.0
        )
    else:
        features["goal_tag_match"] = 0.0


    # --------------------------------------------------
    # 5️⃣ Macro Density (Protein Efficiency)
    # --------------------------------------------------
    if recipe.calories > 0:
        density = recipe.protein / recipe.calories
        # Scale roughly into 0–1 range (assuming 0.3 as high density)
        features["macro_density"] = min(density / 0.3, 1.0)
    else:
        features["macro_density"] = 0.0


    return features
