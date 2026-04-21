"""
engine.py
AI orchestration layer.
Pure decision engine entry point.
"""

from typing import List, Dict

from app.ai.explanation_engine import generate_explanation
from app.ai.scoring_config import SCORING_WEIGHTS
from app.ai.contracts.user_contract import UserContract

from app.ai.contracts.recipe_contract import RecipeContract
from app.ai.contracts.request_contract import RequestContract
from app.ai.contracts.output_contract import RecommendationOutput
from app.ai.validator import validate_request, validate_recipes
from app.ai.constraint_engine import apply_constraints
from app.ai.feature_engine import compute_features
from app.ai.ranking_engine import rank_recipes

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
    user_contract = UserContract(**user)
    
    # Convert recipes to contracts
    recipe_contracts = [RecipeContract(**r) for r in recipes]

    # Validate input
    validate_request(request_contract)
    validate_recipes(recipe_contracts)

    # Apply hard constraints
    filtered = apply_constraints( 
        recipes=[r.model_dump() for r in recipe_contracts],
        request=request_contract,
        user=user_contract
    )

    if not filtered:
        return []

    # Convert filtered dicts back to RecipeContract
    filtered_contracts = [RecipeContract(**r) for r in filtered]

    # Compute features
    recipe_feature_pairs = []

    for recipe in filtered_contracts:
        features = compute_features(recipe, request_contract, user_contract)

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

        explanation = generate_explanation(
            recipe=recipe,
            user=user_contract,
            features=features,
            score=score,
            weights=SCORING_WEIGHTS
        )

        results.append({
            "id": recipe.id,
            "name": recipe.name,
            "calories": recipe.calories,
            "protein": recipe.protein,
            "score": score,

            "nutrition_analysis": explanation["nutrition_analysis"],
            "score_breakdown": explanation["score_breakdown"],
            "summary": explanation["summary"]
    })

    return results

