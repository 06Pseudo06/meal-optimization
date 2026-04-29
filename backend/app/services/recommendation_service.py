from sqlalchemy.orm import Session
import json

from app.models.recipe import Recipe 
from app.models.recommendation_log import RecommendationLog
from app.schemas.recommendation import RecommendationRequest
from app.models.association import RecipeIngredient 

from app.ai.engine import RecommendationEngine

engine = RecommendationEngine()

def get_recommendations(user_input, db):
    try:
        ai_input = {
            "query": getattr(user_input, "query", "") or "",
            "user_id": getattr(user_input, "user_id", None),
        
            "preferences": {
                "diet_type": getattr(user_input, "diet_type", ""),
                "ingredients": getattr(user_input, "ingredients", [])
            },
        
            "constraints": {
                "calorie_max": getattr(user_input, "calorie_max", None),
                "protein_min": getattr(user_input, "protein_min", None)
            }
        }

        results = engine.run(ai_input, db)

        # Validate output format
        if not isinstance(results, list):
            raise ValueError("AI output must be a list")

        return results

    except Exception as e:
        print(f"[AI ERROR]: {e}")
        return fallback_recommendations(db)

def fallback_recommendations(db):
    from app.models.recipe import Recipe
    return db.query(Recipe).limit(5).all()

def recommend_recipes(
    db: Session,
    request: RecommendationRequest,
    user_id: int
):
    # Adapter to not break existing endpoint
    request_dict = request.model_dump()
    class RequestWrapper:
        def __init__(self, d):
            for k, v in d.items():
                setattr(self, k, v)
            self.user_id = user_id
            
    user_input = RequestWrapper(request_dict)
    
    results = get_recommendations(user_input, db)
    
    try:
        # 4️ Extract IDs
        # Fallback returns objects, AI returns dicts
        recipe_ids = [r.id if hasattr(r, 'id') else r["id"] for r in results]

        # 5️ Save recommendation log
        log = RecommendationLog(
            user_id=user_id,
            ingredients=json.dumps(request.ingredients) if hasattr(request, 'ingredients') else "[]",
            recommended_recipe_ids=json.dumps(recipe_ids)
        )

        db.add(log)
        db.commit()
    except Exception as e:
        print(f"Failed to log recommendation: {e}")
        
    return results