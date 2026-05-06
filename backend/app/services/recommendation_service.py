from sqlalchemy.orm import Session
import json

from app.models.recipe import Recipe 
from app.models.recommendation_log import RecommendationLog
from app.schemas.recommendation import RecommendationRequest
from app.models.association import RecipeIngredient 

from app.ai.engine import RecommendationEngine

from app.models.user_profile import UserProfile
from app.models.user_history import UserHistory

import time

# In-memory storage for conversational context per user
USER_MEMORY = {}

def get_user_memory(user_id):
    current_time = time.time()
    if user_id not in USER_MEMORY:
        USER_MEMORY[user_id] = {
            "persistent": {
                "diet_type": None,
                "allergies": [],
                "cuisine": None
            },
            "temporary": {
                "ingredients": [],
                "protein_min": None,
                "protein_max": None,
                "calorie_min": None,
                "calorie_max": None,
                "modifiers": [],
                "turn_count": 0,
                "last_active": current_time
            }
        }
        print(json.dumps({"event": "memory_created", "level": "INFO"}))
    else:
        # Memory Expiration Logic: decay temporary after 30 mins
        if current_time - USER_MEMORY[user_id]["temporary"].get("last_active", current_time) > 1800:
            print(json.dumps({"event": "memory_expired", "reason": "timeout_decay", "level": "INFO"}))
            USER_MEMORY[user_id]["temporary"] = {
                "ingredients": [],
                "protein_min": None,
                "protein_max": None,
                "calorie_min": None,
                "calorie_max": None,
                "modifiers": [],
                "turn_count": 0,
                "last_active": current_time
            }
        else:
            USER_MEMORY[user_id]["temporary"]["last_active"] = current_time
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

def merge_intent(memory, new):
    NON_VEG = ["chicken", "egg", "eggs", "fish", "meat", "beef", "pork"]
    
    persistent = memory["persistent"]
    temporary = memory["temporary"]
    
    merged_persistent = dict(persistent)
    merged_temporary = dict(temporary)
    
    # 1. Ingredient overwrite
    if new.get("ingredients"):
        merged_temporary["ingredients"] = list(set([str(i).lower().strip() for i in (merged_temporary["ingredients"] + new["ingredients"]) if i]))
        print(json.dumps({"event": "memory_updated", "level": "INFO", "field": "ingredients"}))
        
    # 2. Diet override
    if new.get("diet_type"):
        merged_persistent["diet_type"] = str(new["diet_type"]).lower().strip()
        print(json.dumps({"event": "memory_updated", "level": "INFO", "field": "diet_type"}))
        
    # 3. Conflict resolution priority
    if merged_persistent.get("diet_type") == "veg":
        # Vegetarian overrides chicken preference
        if merged_temporary.get("ingredients"):
            filtered = [i for i in merged_temporary["ingredients"] if i not in NON_VEG]
            if len(filtered) < len(merged_temporary["ingredients"]):
                print(json.dumps({"event": "memory_conflict_resolved", "level": "INFO", "resolution": "vegetarian_overrides_meat"}))
            merged_temporary["ingredients"] = filtered
            
    if merged_temporary.get("ingredients"):
        if any(i in NON_VEG for i in merged_temporary["ingredients"]):
            if merged_persistent.get("diet_type") == "veg":
                print(json.dumps({"event": "memory_conflict_resolved", "level": "INFO", "resolution": "meat_ingredient_overrides_veg_diet"}))
            merged_persistent["diet_type"] = "non_veg"
            
    # 4. Constraints
    if new.get("protein_min") is not None:
        merged_temporary["protein_min"] = new["protein_min"]
        merged_temporary["protein_max"] = None
    elif new.get("protein_max") is not None:
        merged_temporary["protein_max"] = new["protein_max"]
        merged_temporary["protein_min"] = None
        
    if new.get("calorie_min") is not None:
        merged_temporary["calorie_min"] = new["calorie_min"]
        merged_temporary["calorie_max"] = None
    elif new.get("calorie_max") is not None:
        merged_temporary["calorie_max"] = new["calorie_max"]
        merged_temporary["calorie_min"] = None
        
    # 5. Semantic Modifiers Stack
    query_class = new.get("query_class")
    if query_class in ["conversational_refinement", "modifier_update"]:
        # Extract modifiers from query via simple keyword matching since LLM doesn't map them yet
        # Alternatively, assume the engine parses them from the query string
        pass
        
    return {
        "persistent": merged_persistent,
        "temporary": merged_temporary
    }

import uuid
import time

engine = RecommendationEngine()

def get_recommendations(user_input, db):
    orchestration_id = str(uuid.uuid4())
    start_time = time.time()
    print(json.dumps({"event": "orchestration_started", "orchestration_id": orchestration_id}))
    try:
        user_id = getattr(user_input, "user_id", None)
        conversation_memory = get_user_memory(user_id)

        query = getattr(user_input, "query", "") or ""
        q_lower = query.lower()

        # STEP 5 - RESET HANDLING & MEMORY LIMITATION
        # Auto-reset if context becomes too long (limit drift)
        if conversation_memory["temporary"].get("turn_count", 0) > 5 or "reset" in q_lower or "clear" in q_lower:
            print(json.dumps({"event": "memory_pruned", "reason": "turn_limit_or_reset"}))
            USER_MEMORY[user_id]["temporary"] = {
                "ingredients": [],
                "protein_min": None, "protein_max": None,
                "calorie_min": None, "calorie_max": None,
                "modifiers": [],
                "turn_count": 0,
                "last_active": time.time()
            }
            conversation_memory = USER_MEMORY[user_id]
            
        conversation_memory["temporary"]["turn_count"] = conversation_memory["temporary"].get("turn_count", 0) + 1

        from app.ai.intent_parser import parse_query
        new_intent = parse_query(query)
        print("PARSED INTENT (NEW):", new_intent)
        
        # Handle greeting or ambiguity early
        if new_intent.get("query_class") in ["greeting", "ambiguity"]:
            print(json.dumps({"event": "onboarding_response_sent", "orchestration_id": orchestration_id}))
            print(json.dumps({"event": "greeting_rendered"}))
            print(json.dumps({"event": "conversational_response_sent"}))
            print(json.dumps({"event": "frontend_conversation_mode"}))
            
            msg = "Hello! How can I help you with your meal planning today?"
            if new_intent.get("query_class") == "ambiguity":
                msg = "Hi there! Tell me your preferences and I'll help you find a meal."
            return {
                "message": msg,
                "data": [],
                "meta": {
                    "source": "ai", 
                    "reason": "conversational", 
                    "query_class": new_intent["query_class"], 
                    "confidence": 0.9, 
                    "orchestration_id": orchestration_id
                }
            }

        # Handle recommendation_retry
        if new_intent.get("query_class") == "recommendation_retry":
            print(json.dumps({"event": "retry_request_detected", "orchestration_id": orchestration_id}))

        # Merge with memory
        final_intent = merge_intent(conversation_memory, new_intent)
        
        # We need intent to be complete to proceed. If LLM says it's incomplete AND
        # our merged final_intent still doesn't have anything concrete, we ask for more.
        if new_intent.get("intent_complete") is False and not any([
            final_intent["temporary"].get("ingredients"),
            final_intent["persistent"].get("diet_type"),
            final_intent["temporary"].get("protein_min"),
            final_intent["temporary"].get("calorie_max"),
            new_intent.get("tags"),
            new_intent.get("goal")
        ]) and new_intent.get("query_class") not in ["conversational_refinement", "recommendation_retry", "greeting"]:
            return {
                "message": "Do you want high protein, low calorie, or a specific ingredient?",
                "data": [],
                "meta": {"source": "ai", "reason": "no_intent", "query_class": "clarification", "confidence": new_intent.get("_confidence", 0.2), "orchestration_id": orchestration_id}
            }

        # Update Memory
        USER_MEMORY[user_id] = final_intent
        
        # We store current_intent for engine constraints just as new_intent
        current_intent = new_intent
        
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
                "diet_type": final_intent["persistent"]["diet_type"],
                "ingredients": final_intent["temporary"]["ingredients"] if final_intent["temporary"]["ingredients"] else [],
                "current_query_ingredients": current_intent["ingredients"] if current_intent["ingredients"] else [],
                "has_ingredient_intent": bool(final_intent["temporary"]["ingredients"])
            },
        
            "constraints": {
                "calorie_min": final_intent["temporary"]["calorie_min"],
                "calorie_max": final_intent["temporary"]["calorie_max"],
                "protein_min": final_intent["temporary"]["protein_min"],
                "protein_max": final_intent["temporary"]["protein_max"]
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
            print("AI OUTPUT EMPTY")
            print(json.dumps({"event": "fallback_decision", "reason": "ai_output_empty"}))
            return fallback_recommendations(db, reason="strict_filter_empty")

        if results and results[0].get("recipe"):
            update_user_profile(db, user_id, results[0]["recipe"], final_intent)
            confidence = new_intent.get("_confidence", 0.8)
        else:
            confidence = new_intent.get("_confidence", 0.5)

        print(json.dumps({
            "event": "orchestration_completed",
            "orchestration_id": orchestration_id,
            "total_latency_ms": round((time.time() - start_time) * 1000)
        }))

        return {
            "data": results,
            "meta": {"source": "ai", "reason": "normal", "confidence": confidence, "orchestration_id": orchestration_id}
        }

    except Exception as e:
        print(f"[AI ERROR]: {e}")
        return fallback_recommendations(db, reason="server_error")

def fallback_recommendations(db, reason="normal"):
    from app.models.recipe import Recipe
    import random
    recipes = db.query(Recipe).all()
    
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
                    "calorie_alignment": 0.5,
                    "fallback_mode": True
                }
            }],
            "meta": {"source": "fallback", "reason": reason, "confidence": 0.5}
        }

    top = sorted(recipes, key=lambda r: r.protein or 0, reverse=True)[:20]
    random.shuffle(top)

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
                    "calorie_alignment": 0.5,
                    "fallback_mode": True
                }
            }
            for r in top[:5]
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
    
    if results.get("meta", {}).get("reason") in ["no_intent", "greeting", "ambiguity"]:
        return results

    # Final safeguard before normalization
    has_data = bool(results and results.get("data"))
    has_valid_recipes = has_data and any(r.get("recipe", {}) != {} for r in results.get("data", []))
    
    if not has_valid_recipes and results.get("meta", {}).get("reason") not in ["no_intent", "greeting", "ambiguity", "strict_filter_empty"]:
        print(json.dumps({"event": "fallback_decision", "reason": "final_safeguard"}))
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