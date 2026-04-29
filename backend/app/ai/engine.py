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

        # STEP 2: Apply Hard Filters
        preferences = input_data.get("preferences", {})
        constraints = input_data.get("constraints", {})

        # Diet filter
        if preferences.get("diet_type"):
            recipes = [
                r for r in recipes
                if r.diet_type and r.diet_type.lower() == preferences["diet_type"].lower()
            ]

        # Ingredient filter
        if preferences.get("ingredients"):
            recipes = [
                r for r in recipes
                if any(
                    ing.lower() in [
                        ri.ingredient.name.lower()
                        for ri in getattr(r, "ingredients", [])
                        if getattr(ri, "ingredient", None)
                    ]
                    for ing in preferences["ingredients"]
                )
            ]

        # Calorie constraint
        if constraints.get("calorie_max") is not None:
            recipes = [r for r in recipes if r.calories and r.calories <= constraints["calorie_max"]]

        # Protein constraint
        if constraints.get("protein_min") is not None:
            recipes = [r for r in recipes if r.protein and r.protein >= constraints["protein_min"]]

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
                calorie_score = max(0, 500 - calories*2)   # dominant factor
                protein_score = protein * 0.05             # weak tie-breaker
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

        # STEP 6: Sort & Limit
        recipes = sorted(recipes, key=score_recipe, reverse=True)[:10]

        # STEP 7: Logging
        logging.info(f"[AI] Query: {query}")
        logging.info(f"[AI] Recipes after filtering: {len(recipes)}")
        logging.info(f"[AI] Top recipe: {recipes[0].name if recipes else 'None'}")

        # STEP 8: Output
        return [
            {
                "id": r.id,
                "name": r.name,
                "calories": r.calories,
                "protein": r.protein,
                "score": score_recipe(r)
            }
            for r in recipes
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