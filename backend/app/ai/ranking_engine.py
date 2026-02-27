"""
ranking_engine.py
Converts computed features into final score
and returns ranked recommendations.
"""

from typing import List, Dict
from app.ai.contracts.recipe_contract import RecipeContract
from app.ai.scoring_config import SCORING_WEIGHTS


def compute_score(features: Dict[str, float]) -> float:
    """
    Computes weighted score:
    score = Σ(weight × feature_value)
    """
    score = 0.0

    for feature_name, weight in SCORING_WEIGHTS.items():
        score += weight * features.get(feature_name, 0.0)

    return round(score, 6)


def rank_recipes(
    recipe_feature_pairs: List[Dict],
    top_n: int = 5
) -> List[Dict]:
    """
    Expects:
    [
        {
            "recipe": RecipeContract,
            "features": { ... }
        }
    ]

    Returns ranked list with score.
    """

    ranked_results = []

    for item in recipe_feature_pairs:
        recipe = item["recipe"]
        features = item["features"]

        score = compute_score(features)

        ranked_results.append({
            "recipe": recipe,
            "features": features,
            "score": score
        })

    # Sort descending
    ranked_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )


    return ranked_results[:top_n]