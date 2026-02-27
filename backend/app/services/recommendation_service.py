from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.models.recipe import Recipe
from app.models.association import RecipeIngredient
from app.models.ingredient import Ingredient
from app.models.recommendation_log import RecommendationLog
from app.models.user import User

from app.ai.engine import generate_recommendations


def recommend_recipes(db: Session, request, user_id: int) -> List[Dict[str, Any]]:

    # 0 Fetch user profile
    user_profile = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user_profile:
        return []
    
    # Serialize 
    user_dict = {
    "daily_calorie_target": user_profile.daily_calorie_target,
    "daily_protein_target": user_profile.daily_protein_target
    }

    # 1️ Fetch all recipes
    recipes = db.query(Recipe).all()
  

    if not recipes:
        return []

    recipe_ids = [r.id for r in recipes]

    # 2️ Fetch ingredient mappings in one query (keep your optimization)
    mappings = (
        db.query(RecipeIngredient.recipe_id, Ingredient.name)
        .join(Ingredient)
        .filter(RecipeIngredient.recipe_id.in_(recipe_ids))
        .all()
    )

    # 3️ Build ingredient map
    recipe_ingredient_map = {}

    for recipe_id, ingredient_name in mappings:
        recipe_ingredient_map.setdefault(recipe_id, []).append(ingredient_name)

    # 4️ Serialize recipes for AI
    recipe_dicts = []

    for recipe in recipes:

        recipe_dict = {
            "id": recipe.id,
            "name": recipe.name,
            "calories": recipe.calories,
            "protein": recipe.protein,
            "carbs": recipe.carbs,
            "fats": recipe.fats,
            "diet_type": recipe.diet_type,
            "ingredients": recipe_ingredient_map.get(recipe.id, []),
            "tags": recipe.tags,
        }

        recipe_dicts.append(recipe_dict)

    # 5️ Call AI layer
    results = generate_recommendations(
        user=user_dict,  
        recipes=recipe_dicts,
        request=request.model_dump()
    )

    # 6️ Log recommendations
    recommended_ids = [r["id"] for r in results]

    log_entry = RecommendationLog(
        request_payload=request.model_dump(),
        recommended_recipe_ids=recommended_ids
    )

    db.add(log_entry)
    db.commit()

    return results
