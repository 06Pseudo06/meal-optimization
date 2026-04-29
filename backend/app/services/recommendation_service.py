from sqlalchemy.orm import Session
import json

from app.models.recipe import Recipe 
from app.models.recommendation_log import RecommendationLog
from app.schemas.recommendation import RecommendationRequest
from app.models.association import RecipeIngredient 

from app.ai.engine import RecommendationEngine

def normalize_recommendation(item):
    if not isinstance(item, dict):
        item = {}
    return {
        "recipe": item.get("recipe", {}),
        "score": item.get("score", 0.0),
        "explanation": {
            "ingredient_alignment": item.get("explanation", {}).get("ingredient_alignment", 0.0),
            "protein_alignment": item.get("explanation", {}).get("protein_alignment", 0.0),
            "calorie_alignment": item.get("explanation", {}).get("calorie_alignment", 0.0),
        }
    }

engine = RecommendationEngine()

def get_recommendations(user_input, db):
    try:
        query = getattr(user_input, "query", "") or ""
        ingredients = getattr(user_input, "ingredients", []) or []
        if not ingredients:
            ingredients = []
            
        protein_min = getattr(user_input, "protein_min", None)
        
        # --- NLP Extraction logic ---
        q_lower = query.lower()
        if "egg" in q_lower:
            ingredients.append("eggs")
        if "high protein" in q_lower:
            protein_min = 30
        
        import re
        match = re.search(r'(\d+)g protein', q_lower)
        if match:
            protein_min = int(match.group(1))
            
        ai_input = {
            "query": query,
            "user_id": getattr(user_input, "user_id", None),
        
            "preferences": {
                "diet_type": getattr(user_input, "diet_type", ""),
                "ingredients": ingredients,
                "has_ingredient_intent": len(ingredients) > 0
            },
        
            "constraints": {
                "calorie_max": getattr(user_input, "calorie_max", None),
                "protein_min": protein_min
            }
        }
        
        print("PARSED USER INPUT:", ai_input)
        print("AI INPUT:", ai_input)

        results = engine.run(ai_input, db)
        
        print("RAW AI OUTPUT:", results)

        # Validate output format
        if not isinstance(results, list):
            raise ValueError("AI output must be a list")

        return results

    except Exception as e:
        print(f"[AI ERROR]: {e}")
        return fallback_recommendations(db)

def fallback_recommendations(db):
    from app.models.recipe import Recipe
    recipes = db.query(Recipe).limit(5).all()
    
    if not recipes:
        return [
            {
                "recipe": {
                    "id": 999,
                    "name": "Fallback High Protein Meal",
                    "calories": 400.0,
                    "protein": 35.0
                },
                "score": 1.0,
                "explanation": {
                    "ingredient_alignment": 0.5,
                    "protein_alignment": 0.5,
                    "calorie_alignment": 0.5
                }
            }
        ]

    return [
        {
            "recipe": {
                "id": r.id,
                "name": r.name,
                "calories": r.calories,
                "protein": r.protein
            },
            "score": 1.0,
            "explanation": {
                "ingredient_alignment": 0.5,
                "protein_alignment": 0.5,
                "calorie_alignment": 0.5
            }
        }
        for r in recipes
    ]

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
    
    # Final safeguard before normalization
    if not results or all(r.get("recipe", {}) == {} for r in results):
        results = fallback_recommendations(db)
    
    # 3️ Normalize all results to guarantee strict structure
    results = [normalize_recommendation(r) for r in results]
    
    try:
        # 4️ Extract IDs from nested recipe object
        recipe_ids = [r["recipe"].get("id") for r in results if r.get("recipe") and r["recipe"].get("id")]

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