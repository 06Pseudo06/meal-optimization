import logging
import json
import time
import random
from sklearn.metrics.pairwise import cosine_similarity
from app.ai.embedding_service import get_query_embedding, JsonVectorStore

logging.basicConfig(level=logging.INFO)

INGREDIENT_MAP = {
    "chicken": ["chicken"],
    "egg": ["egg", "omelette", "scrambled"],
    "paneer": ["paneer", "panner", "cottage cheese"],
    "tofu": ["tofu", "soy"]
}

def compute_similarity(query_emb, recipe_emb):
    if not query_emb or not recipe_emb: return 0.0
    return float(cosine_similarity([query_emb], [recipe_emb])[0][0])

class RecommendationEngine:
    def run(self, input_data: dict, db) -> list:
        logging.info(json.dumps({"event": "hybrid_pipeline_started"}))

        from app.models.recipe import Recipe
        from app.models.association import RecipeIngredient
        from sqlalchemy.orm import joinedload

        # STEP 1: Fetch Data
        recipes = (
            db.query(Recipe)
            .options(
                joinedload(Recipe.ingredients)
                .joinedload(RecipeIngredient.ingredient)
            )
            .all()
        )
        
        vector_store = JsonVectorStore(db)

        preferences = input_data.get("preferences", {})
        constraints = input_data.get("constraints", {})
        user_profile = input_data.get("user_profile", {})
        query = (input_data.get("query") or "").lower()

        # Helper functions
        def match_ingredient(recipe, ingredients):
            name = (recipe.name or "").lower()
            for ing in ingredients:
                synonyms = INGREDIENT_MAP.get(ing, [ing])
                if any(s in name for s in synonyms):
                    return True
            return False

        def get_preference_score(recipe):
            score = 0.0
            for ing, freq in user_profile.get("preferred_ingredients", {}).items():
                if ing in recipe.name.lower():
                    score += freq * 0.01
            return min(score, 1.0)

        # STEP 2 & 3: Deterministic Filtering
        candidate_pool = recipes

        current_query_ingredients = preferences.get("current_query_ingredients") or preferences.get("ingredients")
        if current_query_ingredients:
            logging.info(json.dumps({"event": "ingredient_filter_started", "ingredients": current_query_ingredients}))
            ingredient_filtered = [r for r in candidate_pool if match_ingredient(r, current_query_ingredients)]
            
            if ingredient_filtered:
                candidate_pool = ingredient_filtered
            else:
                logging.warning(json.dumps({"event": "ingredient_candidates_empty", "ingredients": current_query_ingredients}))
                candidate_pool = []
            
            logging.info(json.dumps({"event": "ingredient_candidates_found", "count": len(candidate_pool)}))

        if candidate_pool and preferences.get("diet_type"):
            diet_filtered = [
                r for r in candidate_pool
                if r.diet_type and r.diet_type.lower() == preferences["diet_type"].lower()
            ]
            if diet_filtered:
                candidate_pool = diet_filtered
            else:
                logging.info(json.dumps({"event": "diet_filter_ignored", "reason": "would_empty_pool"}))
            
        logging.info(json.dumps({"event": "deterministic_pool_size", "count": len(candidate_pool)}))
        
        if not candidate_pool:
            logging.info(json.dumps({"event": "fallback_triggered", "reason": "deterministic_pool_empty"}))
            logging.info(json.dumps({"event": "fallback_decision", "reason": "deterministic_pool_empty"}))
            return self._fallback(db, user_profile, current_query_ingredients, preferences.get("diet_type"))
        else:
            logging.info(json.dumps({"event": "deterministic_pool_validated"}))
            logging.info(json.dumps({"event": "fallback_blocked_due_to_valid_candidates"}))
            
        recipes = candidate_pool

        # STEP 4: Semantic Candidate Retrieval (Stage 1)
        logging.info(json.dumps({"event": "semantic_stage_entered"}))
        logging.info(json.dumps({"event": "semantic_retrieval_started"}))
        query_emb = get_query_embedding(query)
        
        candidates = []
        for r in recipes:
            r_emb = vector_store.get_embedding(r.id)
            sem_score = 0.0
            if query_emb and r_emb:
                sem_score = compute_similarity(query_emb, r_emb)
            candidates.append({"recipe": r, "semantic_score": sem_score})
            
        # Sort by semantic similarity and keep top candidates for ranking
        candidates.sort(key=lambda x: x["semantic_score"], reverse=True)
        top_candidates = candidates[:50]  # Narrowed pool
        
        logging.info(json.dumps({"event": "semantic_retrieval_completed", "candidate_pool": len(top_candidates)}))
        # Log top semantic candidates for debugging
        top_candidate_names = [c["recipe"].name for c in top_candidates[:5]]
        logging.info(json.dumps({"event": "top_semantic_candidates", "candidates": top_candidate_names}))

        # NLP Signals
        signals = {
            "high_protein": "protein" in query or "muscle" in query or "gym" in query,
            "low_calorie": "low calorie" in query or "weight loss" in query or "diet" in query or "light" in query,
            "healthy": "health" in query,
            "quick": "quick" in query or "fast" in query,
            "easy": "easy" in query or "easier" in query,
            "budget": "budget" in query or "cheap" in query,
            "spicy": "spicy" in query or "spice" in query,
        }

        # STEP 5: Deterministic Ranking & Diversity (Stage 2)
        logging.info(json.dumps({"event": "ranking_stage_entered"}))
        ranked_recipes = []
        recent_ids = [h["recipe_id"] for h in user_profile.get("history", [])[-15:]]
        seen_clusters = set()

        for cand in top_candidates:
            r = cand["recipe"]
            semantic_score = max(0.0, cand["semantic_score"]) # 0.0 to 1.0
            
            # Ingredient Score (If it survived step 2, it matches or we had none)
            ingredient_score = 0.0
            if current_query_ingredients:
                ingredient_score = 1.0 # Absolute authority dominates ranking

            # Nutrition Score
            p_align = 0.5
            if constraints.get("protein_min"):
                p_align = 1.0 if (r.protein and r.protein >= constraints["protein_min"]) else 0.0
            elif constraints.get("protein_max"):
                p_align = 1.0 if (r.protein and r.protein <= constraints["protein_max"]) else 0.0
            elif signals["high_protein"]:
                p_align = 0.95 if (r.protein and r.protein >= 20) else 0.2

            c_align = 0.5
            if constraints.get("calorie_max"):
                c_align = 1.0 if (r.calories and r.calories <= constraints["calorie_max"]) else 0.0
            elif constraints.get("calorie_min"):
                c_align = 1.0 if (r.calories and r.calories >= constraints["calorie_min"]) else 0.0
            elif signals["low_calorie"]:
                c_align = 0.95 if (r.calories and r.calories <= 450) else 0.2
                
            nutrition_score = (p_align + c_align) / 2.0

            # Personalization Score
            personalization_score = get_preference_score(r)

            # Health Score
            health_score = 0.5
            if getattr(r, "health_score", None) is not None:
                health_score = r.health_score
            if signals["healthy"] and health_score < 0.6:
                health_score = 0.0 # Strict penalty if healthy requested but it isn't
                
            # Difficulty Score
            difficulty_score = 0.5
            if signals["easy"]:
                diff = getattr(r, "difficulty", "") or ""
                difficulty_score = 1.0 if diff.lower() in ["easy", "beginner"] else 0.0
            elif signals["quick"]:
                difficulty_score = 1.0 if getattr(r, "is_quick", False) else 0.0

            # Diversity & Freshness Score
            diversity_score = 0.8
            if r.id in recent_ids:
                diversity_score = 0.0 # Heavy penalty for repeats
                
            # Cluster penalty (penalize if similar recipe already scored highly)
            cluster_key = f"{(r.cuisine or 'none').lower()}_{(getattr(r, 'meal_type', None) or 'none').lower()}"
            if cluster_key in seen_clusters:
                diversity_score *= 0.5 # Halve diversity score if cluster seen
                logging.info(json.dumps({"event": "duplicate_semantic_cluster_penalized", "recipe": r.name}))
            seen_clusters.add(cluster_key)

            # Final Normalized Score
            final_score = (
                ingredient_score * 0.30 +
                semantic_score * 0.25 +
                nutrition_score * 0.15 +
                diversity_score * 0.10 +
                personalization_score * 0.10 +
                health_score * 0.05 +
                difficulty_score * 0.05
            )
            
            # Recalibrated Confidence Calculation
            raw_breakdown = {
                "ingredient_score": ingredient_score,
                "semantic_score": semantic_score,
                "nutrition_score": nutrition_score
            }
            logging.info(json.dumps({"event": "raw_score_breakdown", "recipe": r.name, "scores": raw_breakdown}))
            
            base_conf = ingredient_score * 0.4 + semantic_score * 0.4 + nutrition_score * 0.2
            
            if current_query_ingredients and ingredient_score >= 1.0:
                base_conf = max(base_conf, 0.85)
            elif semantic_score > 0.50:
                sem_conf = 0.55 + (semantic_score - 0.50) * 0.6 # Maps 0.5-1.0 to 0.55-0.85
                base_conf = max(base_conf, sem_conf)

            confidence = min(max(base_conf, 0.0), 1.0)
            
            logging.info(json.dumps({"event": "normalized_confidence_breakdown", "recipe": r.name, "confidence": confidence}))
            logging.info(json.dumps({"event": "confidence_reasoning", "recipe": r.name, "reason": "recalibrated"}))

            # Confidence band assignment
            if confidence >= 0.80:
                band = "High Confidence"
            elif confidence >= 0.55:
                band = "Good Match"
            elif confidence >= 0.35:
                band = "Approximate Match"
            else:
                band = "True Fallback"

            logging.info(json.dumps({
                "event": "confidence_calculated",
                "recipe": r.name,
                "confidence_score": round(confidence, 4)
            }))
            logging.info(json.dumps({
                "event": "confidence_band_assigned",
                "recipe": r.name,
                "band": band
            }))
            
            # Explainability Generation
            reasons = []
            if ingredient_score > 0.8:
                reasons.append("it matches your requested ingredients perfectly")
            if semantic_score > 0.7:
                reasons.append("it strongly aligns with your semantic query")
            if p_align > 0.8 and signals["high_protein"]:
                reasons.append("it is an excellent high-protein option")
            if c_align > 0.8 and signals["low_calorie"]:
                reasons.append("it fits perfectly within your low-calorie diet")
            if difficulty_score > 0.8 and (signals["easy"] or signals["quick"]):
                reasons.append("it is quick and easy to prepare")
            if health_score > 0.8 and signals["healthy"]:
                reasons.append("it is a highly rated healthy choice")
                
            explanation_str = "This recipe was selected because " + ", and ".join(reasons) + "."
            if not reasons:
                explanation_str = "This recipe was selected because it is a solid overall match for your preferences."

            ranked_recipes.append({
                "recipe_obj": r,
                "score": final_score,
                "confidence": confidence,
                "explanation_text": explanation_str,
                "metrics": {
                    "ingredient_alignment": ingredient_score,
                    "protein_alignment": p_align,
                    "calorie_alignment": c_align,
                    "semantic_score": semantic_score,
                    "diversity_score": diversity_score
                }
            })

        # STEP 5: Sort & Limit
        ranked_recipes.sort(key=lambda x: x["score"], reverse=True)
        top_scored = ranked_recipes[:10]
        
        logging.info(json.dumps({"event": "hybrid_ranking_completed"}))

        if not top_scored:
            logging.info(json.dumps({"event": "fallback_decision", "reason": "no_semantically_relevant_recipes"}))
            return self._fallback(db, user_profile, current_query_ingredients, preferences.get("diet_type"))

        # STEP 6: Output Format
        return [
            {
                "recipe": {
                    "id": x["recipe_obj"].id,
                    "name": x["recipe_obj"].name,
                    "calories": x["recipe_obj"].calories,
                    "protein": x["recipe_obj"].protein,
                    "carbs": x["recipe_obj"].carbs,
                    "fats": x["recipe_obj"].fats,
                    "diet_type": x["recipe_obj"].diet_type,
                    "tags": x["recipe_obj"].tags,
                    "is_quick": x["recipe_obj"].is_quick,
                    "is_gym_friendly": x["recipe_obj"].is_gym_friendly
                },
                "score": round(x["score"], 4),
                "confidence": round(x["confidence"], 4),
                "explanation_text": x["explanation_text"],
                "explanation": x["metrics"]
            }
            for x in top_scored
        ]

    def _fallback(self, db, user_profile=None, requested_ingredients=None, requested_diet=None):
        logging.info("[AI Engine] Using fallback recommendations")
        from app.models.recipe import Recipe
        recipes = db.query(Recipe).all()
        
        # In fallback, try to satisfy ingredients if possible
        if requested_ingredients:
            def match_ing(r):
                name = (r.name or "").lower()
                for ing in requested_ingredients:
                    synonyms = INGREDIENT_MAP.get(ing, [ing])
                    if any(s in name for s in synonyms):
                        return True
                return False
            ingredient_pool = [r for r in recipes if match_ing(r)]
            if ingredient_pool:
                recipes = ingredient_pool
                
        # If chicken is requested, never return veg meals
        if requested_ingredients and any(i in ["chicken", "egg", "meat"] for i in requested_ingredients):
            recipes = [r for r in recipes if r.diet_type and r.diet_type.lower() != "veg"]
            
        top = sorted(recipes, key=lambda r: r.protein or 0, reverse=True)[:50]
        
        if user_profile:
            recent_ids = [h["recipe_id"] for h in user_profile.get("history", [])[-15:]]
            top = [r for r in top if r.id not in recent_ids]
            if not top:
                top = recipes[:50]
                
        random.shuffle(top)

        return [
            {
                "recipe": {
                    "id": r.id,
                    "name": r.name,
                    "calories": r.calories,
                    "protein": r.protein,
                    "carbs": r.carbs,
                    "fats": r.fats,
                    "diet_type": r.diet_type,
                    "tags": r.tags,
                    "is_quick": r.is_quick,
                    "is_gym_friendly": r.is_gym_friendly
                },
                "score": 1.0,
                "confidence": 0.4,
                "explanation_text": "This recipe was selected as a diverse alternative based on our top nutritional options.",
                "explanation": {
                    "ingredient_alignment": 0.5,
                    "protein_alignment": 0.5,
                    "calorie_alignment": 0.5,
                    "fallback_mode": True
                }
            }
            for r in top[:5]
        ]