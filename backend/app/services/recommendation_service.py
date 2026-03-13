from sqlalchemy.orm import Session
import json

from app.models.recipe import Recipe 
from app.models.recommendation_log import RecommendationLog
from app.schemas.recommendation import RecommendationRequest
from app.models.association import RecipeIngredient 

from app.ai.engine import generate_recommendations


def recommend_recipes(
    db: Session,
    request: RecommendationRequest,
    user_id: int
):

    # 1️ Fetch recipes
    from sqlalchemy.orm import joinedload

    recipes = (
        db.query(Recipe)
        .options(
            joinedload(Recipe.ingredients)
            .joinedload(RecipeIngredient.ingredient))
        .all()
    )

    # 2️ Convert DB objects → AI dictionaries
    recipe_dicts = []

    for r in recipes:

        ingredient_names = [
            ri.ingredient.name
            for ri in r.ingredients
        ]

        recipe_dicts.append({
            "id": r.id,
            "name": r.name,
            "calories": r.calories,
            "protein": r.protein,
            "diet_type": r.diet_type,
            "tags": r.tags,
            "ingredients": ingredient_names
        })


    print(recipe_dicts[:3])
    
    # 3️ Run AI engine
    results = generate_recommendations(
        user={"id": user_id},
        recipes=recipe_dicts,
        request=request.model_dump()
    )

    # 4️ Extract IDs
    recipe_ids = [r["id"] for r in results]

    # 5️ Save recommendation log
    log = RecommendationLog(
        user_id=user_id,
        ingredients=json.dumps(request.ingredients),
        recommended_recipe_ids=json.dumps(recipe_ids)
    )

    db.add(log)
    db.commit()

    # 6️ Return results
    return results 