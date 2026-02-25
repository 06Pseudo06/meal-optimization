"""
engine.py
AI orchestration layer.
Pure decision engine entry point.
"""

from typing import List, Dict

from AI.contracts.recipe_contract import RecipeContract
from AI.contracts.request_contract import RequestContract
from AI.contracts.output_contract import RecommendationOutput
from AI.validator import validate_request, validate_recipes
from AI.constraint_engine import apply_constraints
from AI.feature_engine import compute_features
from AI.ranking_engine import rank_recipes


def generate_recommendations(
    user: Dict,              # currently unused (future personalization)
    recipes: List[Dict],
    request: Dict
) -> List[Dict]:
    """
    Main AI entry point.
    Returns plain list of recommendations.
    """

    # Convert request to contract
    request_contract = RequestContract(**request)

    # Convert recipes to contracts
    recipe_contracts = [RecipeContract(**r) for r in recipes]

    # Validate input
    validate_request(request_contract)
    validate_recipes(recipe_contracts)

    # Apply hard constraints
    filtered = apply_constraints(
        recipes=[r.model_dump() for r in recipe_contracts],
        request=request_contract
    )

    if not filtered:
        return []

    # Convert filtered dicts back to RecipeContract
    filtered_contracts = [RecipeContract(**r) for r in filtered]

    # Compute features
    recipe_feature_pairs = []

    for recipe in filtered_contracts:
        features = compute_features(recipe, request_contract)

        recipe_feature_pairs.append({
            "recipe": recipe,
            "features": features
        })

    # Rank recipes
    ranked = rank_recipes(recipe_feature_pairs)

    # Format final output (NO wrapper object)
    results = []

    for item in ranked:
        recipe = item["recipe"]
        features = item["features"]
        score = item["score"]

        results.append({
            "id": recipe.id,
            "name": recipe.name,
            "calories": recipe.calories,
            "protein": recipe.protein,
            "score": score,
            "explanation": features   # IMPORTANT: explanation not features
        })

    return results

