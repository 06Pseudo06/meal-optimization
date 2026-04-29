from sqlalchemy.orm import Session
import json

from app.models.recipe import Recipe 
from app.models.recommendation_log import RecommendationLog
from app.schemas.recommendation import RecommendationRequest
from app.models.association import RecipeIngredient 

from app.ai.engine import RecommendationEngine

from app.models.user_profile import UserProfile
from app.models.user_history import UserHistory

# In-memory storage for conversational context per user
USER_MEMORY = {}

def get_user_memory(user_id):
    if user_id not in USER_MEMORY:
        USER_MEMORY[user_id] = {
            "ingredients": None,
            "diet_type": None,
            "protein_min": None,
            "protein_max": None,
            "calorie_min": None,
            "calorie_max": None
        }
    return USER_MEMORY[user_id]

def get_user_profile(db, user_id):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id, preferred_ingredients={})
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

def update_user_profile(db, user_id, recipe, intent):
    import time
    history_entry = UserHistory(
        user_id=user_id,
        recipe_id=recipe.get("id"),
        timestamp=int(time.time()),
        liked=True
    )
    db.add(history_entry)

    profile = get_user_profile(db, user_id)
    prefs = dict(profile.preferred_ingredients) if profile.preferred_ingredients else {}
    for ing in intent.get("ingredients", []) or []:
        prefs[ing] = prefs.get(ing, 0) + 1
    profile.preferred_ingredients = prefs
    
    db.commit()
    
    from sqlalchemy import text
    try:
        db.execute(
            text("""
            DELETE FROM user_history 
            WHERE user_id = :user_id 
            AND id NOT IN (
                SELECT id FROM user_history 
                WHERE user_id = :user_id 
                ORDER BY timestamp DESC 
                LIMIT 100
            )
            """),
            {"user_id": user_id}
        )
        db.commit()
    except Exception as e:
        print("Failed to prune user history:", e)

NON_VEG = ["chicken", "egg", "eggs", "fish", "meat", "beef", "pork"]

def resolve_intent(current_intent, memory_intent):
    if current_intent.get("ingredients"):
        final_intent = {
            "ingredients": current_intent["ingredients"],
            "diet_type": current_intent.get("diet_type"),
            "protein_min": current_intent.get("protein_min"),
            "protein_max": current_intent.get("protein_max"),
            "calorie_min": current_intent.get("calorie_min"),
            "calorie_max": current_intent.get("calorie_max")
        }
    else:
        final_intent = {
            "ingredients": current_intent.get("ingredients") if current_intent.get("ingredients") else memory_intent.get("ingredients"),
            "diet_type": current_intent.get("diet_type") if current_intent.get("diet_type") else memory_intent.get("diet_type"),
            "protein_min": current_intent.get("protein_min") if current_intent.get("protein_min") else memory_intent.get("protein_min"),
            "protein_max": current_intent.get("protein_max") if current_intent.get("protein_max") else memory_intent.get("protein_max"),
            "calorie_min": current_intent.get("calorie_min") if current_intent.get("calorie_min") else memory_intent.get("calorie_min"),
            "calorie_max": current_intent.get("calorie_max") if current_intent.get("calorie_max") else memory_intent.get("calorie_max"),
        }

    # RULE 3 - CONFLICT MATRIX
    if final_intent.get("ingredients"):
        if any(i in NON_VEG for i in final_intent["ingredients"]):
            final_intent["diet_type"] = None

    if current_intent.get("diet_type") == "veg":
        final_intent["diet_type"] = "veg"
        if final_intent.get("ingredients"):
            final_intent["ingredients"] = [i for i in final_intent["ingredients"] if i not in NON_VEG]
            if not final_intent["ingredients"]:
                final_intent["ingredients"] = None

    if current_intent.get("protein_max"):
        final_intent["protein_min"] = None
    if current_intent.get("protein_min"):
        final_intent["protein_max"] = None
    if current_intent.get("calorie_max"):
        final_intent["calorie_min"] = None
    if current_intent.get("calorie_min"):
        final_intent["calorie_max"] = None

    return final_intent

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
        user_id = getattr(user_input, "user_id", None)
        conversation_memory = get_user_memory(user_id)

        query = getattr(user_input, "query", "") or ""
        q_lower = query.lower()

        # STEP 5 - RESET HANDLING
        if any(word in q_lower for word in ["reset", "start over", "anything", "clear"]):
            USER_MEMORY[user_id] = {
                "ingredients": None, "diet_type": None,
                "protein_min": None, "protein_max": None,
                "calorie_min": None, "calorie_max": None
            }
            conversation_memory = USER_MEMORY[user_id]

        current_intent = {
            "ingredients": None, "diet_type": None,
            "protein_min": None, "protein_max": None,
            "calorie_min": None, "calorie_max": None
        }

        # --- NLP Extraction logic ---
        INGREDIENT_SYNONYMS = {
            "egg": ["egg", "omelette", "scrambled", "eggs"],
            "chicken": ["chicken", "grilled chicken"],
            "paneer": ["paneer", "cottage cheese", "panner"],
            "tofu": ["tofu", "soy"]
        }

        extracted_ingredients = []
        for key, synonyms in INGREDIENT_SYNONYMS.items():
            if any(syn in q_lower for syn in synonyms):
                extracted_ingredients = [key]
                break

        if extracted_ingredients:
            current_intent["ingredients"] = extracted_ingredients
            conversation_memory["ingredients"] = extracted_ingredients
            
        print("EXTRACTED INGREDIENT:", extracted_ingredients)

        if "low protein" in q_lower or "less protein" in q_lower:
            current_intent["protein_max"] = 15
        elif "high protein" in q_lower:
            current_intent["protein_min"] = 30
        
        import re
        match = re.search(r'(\d+)g protein', q_lower)
        if match:
            current_intent["protein_min"] = int(match.group(1))

        if "high calorie" in q_lower:
            current_intent["calorie_min"] = 600
        elif "low calorie" in q_lower or "weight loss" in q_lower:
            current_intent["calorie_max"] = 400

        if "veg recipe" in q_lower or "veg" in q_lower:
            current_intent["diet_type"] = "veg"
            
        print("CURRENT INTENT:", current_intent)
        print("MEMORY:", conversation_memory)

        final_intent = resolve_intent(current_intent, conversation_memory)
        print("FINAL INTENT:", final_intent)

        # FIX NO-INTENT BUG
        if not any([
            final_intent.get("ingredients"),
            final_intent.get("diet_type"),
            final_intent.get("protein_min")
        ]):
            return fallback_recommendations(db, reason="no_intent")

        # Update Memory
        USER_MEMORY[user_id] = final_intent
        
        user_profile = get_user_profile(db, user_id)
        recent_history = db.query(UserHistory).filter(UserHistory.user_id == user_id).order_by(UserHistory.timestamp.desc()).limit(5).all()

        ai_input = {
            "query": query,
            "user_id": user_id,
            "user_profile": {
                "preferred_ingredients": user_profile.preferred_ingredients,
                "history": [{"recipe_id": h.recipe_id} for h in recent_history]
            },
        
            "preferences": {
                "diet_type": final_intent["diet_type"],
                "ingredients": final_intent["ingredients"] if final_intent["ingredients"] else [],
                "has_ingredient_intent": bool(final_intent["ingredients"])
            },
        
            "constraints": {
                "calorie_min": final_intent["calorie_min"],
                "calorie_max": final_intent["calorie_max"],
                "protein_min": final_intent["protein_min"],
                "protein_max": final_intent["protein_max"]
            }
        }
        
        print("PARSED USER INPUT:", ai_input)
        print("AI INPUT:", ai_input)

        results = engine.run(ai_input, db)
        
        print("RAW AI OUTPUT:", results)

        # Validate output format
        if not isinstance(results, list):
            raise ValueError("AI output must be a list")
            
        if not results or all(not r.get("recipe") for r in results):
            print("AI OUTPUT EMPTY, USING FALLBACK")
            return fallback_recommendations(db, reason="low_confidence")

        if results and results[0].get("recipe"):
            update_user_profile(db, user_id, results[0]["recipe"], final_intent)
            confidence = results[0].get("confidence", 0.8)
        else:
            confidence = 0.5

        return {
            "data": results,
            "meta": {"source": "ai", "reason": "normal", "confidence": confidence}
        }

    except Exception as e:
        print(f"[AI ERROR]: {e}")
        return fallback_recommendations(db, reason="server_error")

def fallback_recommendations(db, reason="normal"):
    from app.models.recipe import Recipe
    recipes = db.query(Recipe).limit(5).all()
    
    if not recipes:
        return {
            "data": [{
                "recipe": {
                    "id": 999,
                    "name": "Fallback High Protein Meal",
                    "calories": 400.0,
                    "protein": 35.0
                },
                "score": 1.0,
                "confidence": 0.5,
                "explanation": {
                    "ingredient_alignment": 0.5,
                    "protein_alignment": 0.5,
                    "calorie_alignment": 0.5
                }
            }],
            "meta": {"source": "fallback", "reason": reason, "confidence": 0.5}
        }

    return {
        "data": [
            {
                "recipe": {
                    "id": r.id,
                    "name": r.name,
                    "calories": r.calories,
                    "protein": r.protein
                },
                "score": 1.0,
                "confidence": 0.5,
                "explanation": {
                    "ingredient_alignment": 0.5,
                    "protein_alignment": 0.5,
                    "calorie_alignment": 0.5
                }
            }
            for r in recipes
        ],
        "meta": {"source": "fallback", "reason": reason, "confidence": 0.5}
    }

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
    if not results or not results.get("data") or all(r.get("recipe", {}) == {} for r in results.get("data", [])):
        results = fallback_recommendations(db, reason="low_confidence")
    
    # 3️ Normalize all results to guarantee strict structure
    results["data"] = [normalize_recommendation(r) for r in results["data"]]
    
    try:
        # 4️ Extract IDs from nested recipe object
        recipe_ids = [r["recipe"].get("id") for r in results["data"] if r.get("recipe") and r["recipe"].get("id")]

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