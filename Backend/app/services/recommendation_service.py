from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.models.recipe import Recipe
from app.models.association import RecipeIngredient
from app.models.ingredient import Ingredient
from app.models.recommendation_log import RecommendationLog

from app.services.constraint_service import apply_constraints
from app.services.feature_service import compute_features
from app.services.ranking_engine import compute_score


def recommend_recipes(db: Session, request) -> List[Dict[str, Any]]:

    # Step 1: Apply constraints
    candidates = apply_constraints(db, request)

    if not candidates:
        return []

    recipe_ids = [r.id for r in candidates]

    # Step 2: Fetch all ingredient mappings in ONE query
    mappings = (
        db.query(RecipeIngredient.recipe_id, Ingredient.name)
        .join(Ingredient)
        .filter(RecipeIngredient.recipe_id.in_(recipe_ids))
        .all()
    )

    # Step 3: Build mapping dict
    recipe_ingredient_map = {}

    for recipe_id, ingredient_name in mappings:
        recipe_ingredient_map.setdefault(recipe_id, set()).add(ingredient_name.lower())

    # Step 4: Compute ranking
    ranked = []

    for recipe in candidates:

        recipe_ingredients = recipe_ingredient_map.get(recipe.id, set())

        features = compute_features(
            recipe=recipe,
            request=request,
            recipe_ingredients=recipe_ingredients
        )

        final_score = compute_score(features)
        ranked.append((recipe, final_score, features))

    ranked.sort(key=lambda x: x[1], reverse=True)

    top_recipes = ranked[:5]

    # Extract recommended IDs
    recommended_ids = [recipe.id for recipe, _, _ in top_recipes]

    # Save log BEFORE returning


    log_entry = RecommendationLog(
        request_payload=request.model_dump(),
        recommended_recipe_ids=recommended_ids
    )

    db.add(log_entry)
    db.commit()

    return [
        {
            "id": recipe.id,
            "name": recipe.name,
            "calories": recipe.calories,
            "protein": recipe.protein,
            "score": round(score, 3),
            "explanation": {
                key: round(value, 3)
                for key, value in features.items()
            }
        }   
        for recipe, score, features in top_recipes
    ]
