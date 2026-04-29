import logging
import math

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print("Warning: Could not load SentenceTransformer:", e)
    embedder = None

logging.basicConfig(level=logging.INFO)
import json
from collections import OrderedDict
import time
import threading

"""
RECIPE_EMBEDDING_CACHE Strategy:
Current: In-memory OrderedDict (LRU cache) for fast single-instance lookups.
Future (Multi-Instance): Replace with Redis or native pgvector/FAISS integration 
inside the compute_similarity() wrapper to share state across horizontal workers.
"""
RECIPE_EMBEDDING_CACHE = OrderedDict()
IN_FLIGHT = {}
MAX_CACHE_SIZE = 1000

def compute_similarity(query_emb, recipe_emb):
    return float(cosine_similarity([query_emb], [recipe_emb])[0][0])

class RecommendationEngine:
    def run(self, input_data: dict, db) -> list:
        logging.info("[AI Engine] Starting AI recommendation pipeline")

        # STEP 1: Fetch Data
        from app.models.recipe import Recipe
        from app.models.association import RecipeIngredient
        from sqlalchemy.orm import joinedload

        recipes = (
            db.query(Recipe)
            .options(
                joinedload(Recipe.ingredients)
                .joinedload(RecipeIngredient.ingredient)
            )
            .all()
        )
        print("DB RESULTS COUNT:", len(recipes))

        # STEP 2: Apply Hard Filters
        preferences = input_data.get("preferences", {})
        constraints = input_data.get("constraints", {})

        # Diet filter
        if preferences.get("diet_type"):
            recipes = [
                r for r in recipes
                if r.diet_type and r.diet_type.lower() == preferences["diet_type"].lower()
            ]

        original_recipes = recipes.copy() # Keep a copy to relax if needed
        fallback_mode = False
        
        # STEP 1 - diet filter
        diet_type = preferences.get("diet_type")
        if diet_type == "veg":
            filtered_diet = [r for r in recipes if r.diet_type and r.diet_type.lower() == "veg"]
            if filtered_diet:
                recipes = filtered_diet

        def matches_ingredient(recipe_name, ingredient):
            return ingredient in recipe_name.lower()

        print("INGREDIENT FILTER APPLIED:", preferences.get("ingredients"))
        print("AVAILABLE RECIPES:", [r.name for r in recipes])

        # STEP 2 - ingredient filter (HARD PRIORITY)
        if preferences.get("ingredients"):
            recipes = [
                r for r in recipes
                if any(matches_ingredient(r.name, ing) for ing in preferences["ingredients"])
            ]

        # Protein constraint
        if constraints.get("protein_min") is not None:
            recipes = [r for r in recipes if r.protein and r.protein >= constraints["protein_min"]]
        if constraints.get("protein_max") is not None:
            recipes = [r for r in recipes if r.protein and r.protein <= constraints["protein_max"]]

        # Calorie constraint
        if constraints.get("calorie_min") is not None:
            recipes = [r for r in recipes if r.calories and r.calories >= constraints["calorie_min"]]
        if constraints.get("calorie_max") is not None:
            recipes = [r for r in recipes if r.calories and r.calories <= constraints["calorie_max"]]

        # STEP 3 - fallback if empty
        if not recipes:
            recipes = original_recipes
            fallback_mode = True
            
        print("FINAL RECIPES:", [r.name for r in recipes])

        # STEP 3: NLP Signals
        query = (input_data.get("query") or "").lower()

        signals = {
            "high_protein": False,
            "low_calorie": False,
            "veg": False,
            "non_veg": False
        }

        if "protein" in query or "muscle" in query or "gym" in query:
            signals["high_protein"] = True

        if "low calorie" in query or "weight loss" in query or "diet" in query:
            signals["low_calorie"] = True

        if "veg" in query or "vegetarian" in query:
            signals["veg"] = True

        if "chicken" in query or "egg" in query or "non veg" in query:
            signals["non_veg"] = True

        # Optional hard cap for low calorie intent
        if signals["low_calorie"]:
            recipes = [r for r in recipes if r.calories and r.calories <= 400]

        # STEP 4: Handle Empty
        if not recipes:
            logging.info("[AI Engine] No recipes matched filters → fallback")
            return self._fallback(db)

        # STEP 5: Scoring
        def score_recipe(r):
            protein = r.protein or 0
            calories = r.calories or 0

            # LOW CALORIE MODE (FIXED)
            if signals["low_calorie"]:
                calorie_score = max(0, 200 - calories)   # dominant factor
                protein_score = protein * 0.1             # weak tie-breaker
                score = calorie_score + protein_score

            else:
                # DEFAULT MODE
                score = (protein * 2) - (calories * 0.05)

                if signals["high_protein"]:
                    score += protein * 2

                if signals["veg"] and r.diet_type and r.diet_type.lower() == "veg":
                    score += 15

                if signals["non_veg"] and r.diet_type and r.diet_type.lower() == "non-veg":
                    score += 15

            # Ensure non-negative
            score = max(0, score)

            return round(score, 2)

        # Precompute query embedding
        query_emb = None
        if embedder and query.strip():
            query_emb = embedder.encode(query)

        user_profile = input_data.get("user_profile", {})

        def get_preference_score(user_profile, recipe):
            score = 0.0
            for ing, freq in user_profile.get("preferred_ingredients", {}).items():
                if ing in recipe.name.lower():
                    score += freq * 0.01
            return min(score, 1.0)

        def get_diversity_score(user_profile, recipe):
            recent_ids = [h["recipe_id"] for h in user_profile.get("history", [])[-5:]]
            return 0.0 if recipe.id in recent_ids else 1.0

        # Cache invalidation and batch computation
        pending = []
        for r in recipes:
            r_updated = getattr(r, "updated_at", 0)
            
            if r.id in RECIPE_EMBEDDING_CACHE:
                cached = RECIPE_EMBEDDING_CACHE[r.id]
                if r_updated > cached["updated_at"]:
                    # Invalidate
                    del RECIPE_EMBEDDING_CACHE[r.id]
                    r.embedding = None
                    logging.info(json.dumps({
                        "event": "embedding_cache_evict",
                        "recipe_id": r.id,
                        "reason": "updated_at_mismatch"
                    }))
                    
            if r.id not in RECIPE_EMBEDDING_CACHE and embedder:
                if r.embedding:
                    if len(RECIPE_EMBEDDING_CACHE) >= MAX_CACHE_SIZE:
                        RECIPE_EMBEDDING_CACHE.popitem(last=False)
                    RECIPE_EMBEDDING_CACHE[r.id] = {"emb": r.embedding, "updated_at": r_updated}
                else:
                    pending.append(r)

        if pending:
            pending_embs = {}
            for r in pending:
                if r.id in IN_FLIGHT:
                    IN_FLIGHT[r.id].wait()
                
                if r.id in RECIPE_EMBEDDING_CACHE:
                    continue
                
                compute_event = threading.Event()
                IN_FLIGHT[r.id] = compute_event
                
                try:
                    desc = getattr(r, "description", "") or ""
                    recipe_text = f"{r.name} {desc}".strip()
                    emb = embedder.encode(recipe_text).tolist()
                    print(f"Embedding computed for recipe: {r.id}")
                    
                    if len(RECIPE_EMBEDDING_CACHE) >= MAX_CACHE_SIZE:
                        RECIPE_EMBEDDING_CACHE.popitem(last=False)
                    r_updated = getattr(r, "updated_at", 0)
                    RECIPE_EMBEDDING_CACHE[r.id] = {"emb": emb, "updated_at": r_updated}
                    pending_embs[r.id] = emb
                except Exception as e:
                    logging.warning(json.dumps({"event": "embedding_compute_error", "recipe_id": r.id, "error": str(e)}))
                finally:
                    compute_event.set()
                    IN_FLIGHT.pop(r.id, None)

            if pending_embs:
                try:
                    locked_recipes = db.query(Recipe).filter(Recipe.id.in_(list(pending_embs.keys()))).with_for_update(skip_locked=True).all()
                    dirty = False
                    for locked_r in locked_recipes:
                        if not locked_r.embedding:
                            locked_r.embedding = pending_embs[locked_r.id]
                            dirty = True
                    if dirty:
                        db.commit()
                        logging.info(json.dumps({
                            "event": "embedding_batch_commit",
                            "count": len(locked_recipes)
                        }))
                except Exception as e:
                    db.rollback()
                    logging.warning(json.dumps({
                        "event": "embedding_batch_commit_error",
                        "error": str(e)
                    }))

        metrics = {
            "cache_hits": len(recipes) - len(pending),
            "cache_misses": len(pending),
            "computations_performed": len(pending_embs) if pending else 0
        }
        
        logging.info(json.dumps({
            "event": "embedding_resolution_complete",
            "cache_hit_rate": round(metrics["cache_hits"] / max(len(recipes), 1), 2),
            **metrics
        }))

        def calc_alignment(r):
            ingredient_align = 0.0
            if preferences.get("ingredients"):
                if any(matches_ingredient(r.name, ing) for ing in preferences["ingredients"]):
                    ingredient_align = 1.0
                    
            p_align = 0.5
            if constraints.get("protein_min"):
                p_align = 1.0 if (r.protein and r.protein >= constraints["protein_min"]) else 0.8
            elif constraints.get("protein_max"):
                p_align = 1.0 if (r.protein and r.protein <= constraints["protein_max"]) else 0.8
            elif signals["high_protein"]:
                p_align = 0.95
                
            c_align = 0.5
            if constraints.get("calorie_max"):
                c_align = 1.0 if (r.calories and r.calories <= constraints["calorie_max"]) else 0.8
            elif constraints.get("calorie_min"):
                c_align = 1.0 if (r.calories and r.calories >= constraints["calorie_min"]) else 0.8
            elif signals["low_calorie"]:
                c_align = 0.95
            
            preference_score = get_preference_score(user_profile, r)
            diversity_score = get_diversity_score(user_profile, r)

            semantic_score = 0.0
            if query_emb is not None and embedder:
                cached = RECIPE_EMBEDDING_CACHE.get(r.id)
                if cached and cached["emb"]:
                    RECIPE_EMBEDDING_CACHE.move_to_end(r.id)
                    semantic_score = compute_similarity(query_emb, cached["emb"])
                    logging.info(json.dumps({
                        "event": "embedding_cache_hit",
                        "recipe_id": r.id,
                        "hit": True
                    }))
            
            if not embedder:
                score = (
                    ingredient_align * 0.45 +
                    p_align * 0.35 +
                    preference_score * 0.1 +
                    diversity_score * 0.1
                )
                confidence = min(max(ingredient_align * 0.6 + p_align * 0.4, 0.0), 1.0)
            else:
                score = (
                    ingredient_align * 0.3 +
                    p_align * 0.2 +
                    semantic_score * 0.3 +
                    preference_score * 0.1 +
                    diversity_score * 0.1
                )
                confidence = min(max(semantic_score * 0.5 + ingredient_align * 0.3 + p_align * 0.2, 0.0), 1.0)
                
            return ingredient_align, p_align, c_align, score, confidence

        # STEP 6: Sort & Limit
        scored_recipes = [{"recipe_obj": r, "metrics": calc_alignment(r)} for r in recipes]
        scored_recipes.sort(key=lambda x: x["metrics"][3], reverse=True)
        top_scored = scored_recipes[:10]

        print("FINAL CANDIDATES:", [x["recipe_obj"].name for x in top_scored])

        if len(top_scored) == 0:
            return self._fallback(db)

        # STEP 7: Logging
        logging.info(f"[AI] Query: {query}")
        logging.info(f"[AI] Recipes after filtering: {len(top_scored)}")
        logging.info(f"[AI] Top recipe: {top_scored[0]['recipe_obj'].name if top_scored else 'None'}")

        # STEP 8: Output
        return [
            {
                "recipe": {
                    "id": x["recipe_obj"].id,
                    "name": x["recipe_obj"].name,
                    "calories": x["recipe_obj"].calories,
                    "protein": x["recipe_obj"].protein,
                },
                "score": x["metrics"][3],
                "confidence": x["metrics"][4],
                "explanation": {
                    "ingredient_alignment": x["metrics"][0],
                    "protein_alignment": x["metrics"][1],
                    "calorie_alignment": x["metrics"][2],
                    "fallback_mode": fallback_mode
                }
            }
            for x in top_scored
        ]

    def _fallback(self, db):
        logging.info("[AI Engine] Using fallback recommendations")
        from app.models.recipe import Recipe

        recipes = db.query(Recipe).limit(5).all()

        return [
            {
                "id": r.id,
                "name": r.name,
                "calories": r.calories,
                "protein": r.protein,
                "score": 1.0
            }
            for r in recipes
        ]