
import logging

logging.basicConfig(level=logging.INFO)


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

        print("INGREDIENT FILTER APPLIED:", preferences.get("ingredients"))

        # Ingredient filter (HARD PRIORITY)
        if preferences.get("ingredients"):
            ingredient_matches = [
                r for r in recipes
                if any(ing.lower() in r.name.lower() for ing in preferences["ingredients"])
            ]
            
            # HARD PRIORITY: only restrict if matches exist
            if ingredient_matches:
                recipes = ingredient_matches
            else:
                recipes = original_recipes # fallback gracefully

        # Calorie constraint
        if constraints.get("calorie_max") is not None:
            recipes = [r for r in recipes if r.calories and r.calories <= constraints["calorie_max"]]

        # Protein constraint
        if constraints.get("protein_min") is not None:
            filtered = [r for r in recipes if r.protein and r.protein >= constraints["protein_min"]]
            if filtered:
                recipes = filtered

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

        def calc_alignment(r):
            ingredient_align = 0.0
            if preferences.get("ingredients"):
                if any(ing.lower() in r.name.lower() for ing in preferences["ingredients"]):
                    ingredient_align = 1.0
                    
            p_align = 0.5
            if constraints.get("protein_min"):
                p_align = 1.0 if (r.protein and r.protein >= constraints["protein_min"]) else 0.8
            elif signals["high_protein"]:
                p_align = 0.95
                
            c_align = 0.5
            if constraints.get("calorie_max"):
                c_align = 1.0 if (r.calories and r.calories <= constraints["calorie_max"]) else 0.8
            elif signals["low_calorie"]:
                c_align = 0.95
            
            score = (ingredient_align * 50) + (p_align * 30) + (c_align * 20)
            return ingredient_align, p_align, c_align, score

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
                "explanation": {
                    "ingredient_alignment": x["metrics"][0],
                    "protein_alignment": x["metrics"][1],
                    "calorie_alignment": x["metrics"][2]
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