"""
explanation_engine.py
---------------------
Generates structured, deterministic explainability for recommendations.
Aligned with backend user targets.
"""

from typing import Dict
from app.ai.contracts.recipe_contract import RecipeContract
from app.ai.contracts.user_contract import UserContract

def clamp(value: float, min_v: float = 0.0, max_v: float = 100.0) -> float:
    return max(min_v, min(value, max_v))


def classify_protein(percent: float) -> str:
    if percent >= 90:
        return "Excellent"
    elif percent >= 70:
        return "Good"
    elif percent >= 40:
        return "Moderate"
    return "Low"


def classify_calories(percent: float) -> str:
    if percent >= 90:
        return "Excellent"
    elif percent >= 70:
        return "Good"
    elif percent >= 40:
        return "Moderate"
    return "Poor"


# ----------------------------
# Main Explainability Function
# ----------------------------

def generate_explanation(
    recipe: RecipeContract,
    user: UserContract,
    features: Dict[str, float],
    score: float,
    weights: Dict[str, float]
) -> Dict:

    # ----------------------------
    # A️⃣ Protein Coverage %
    # ----------------------------
    protein_target = user.daily_protein_target
    protein_percent = clamp((recipe.protein / protein_target) * 100)

    # ----------------------------
    # B️⃣ Calorie Difference
    # ----------------------------
    calorie_target = user.daily_calorie_target
    calorie_difference = recipe.calories - calorie_target

    # ----------------------------
    # C️⃣ Calorie Alignment %
    # ----------------------------
    calorie_alignment_percent = features.get("calorie_alignment", 0) * 100

    # ----------------------------
    # D️⃣ Classification
    # ----------------------------
    protein_class = classify_protein(protein_percent)
    calorie_class = classify_calories(calorie_alignment_percent)

    # ----------------------------
    # E️⃣ Score Breakdown
    # ----------------------------
    score_breakdown = {}
    total_score = score if score != 0 else 1  # prevent division error

    for feature_name, weight in weights.items():
        contribution = (weight * features.get(feature_name, 0)) / total_score
        score_breakdown[f"{feature_name}_contribution_percent"] = round(contribution * 100, 2)

    # ----------------------------
    # F️⃣ Summary (Deterministic)
    # ----------------------------
    if calorie_alignment_percent >= 90 and protein_percent >= 70:
        summary = "Very close to your calorie target and provides strong protein coverage."
    elif calorie_alignment_percent < 50 and protein_percent >= 70:
        summary = "High protein meal but significantly off your calorie target."
    elif protein_percent < 40:
        summary = "Low protein option and may not meet your nutritional needs."
    else:
        summary = "Decent balance between calories and protein."

    # ----------------------------
    # Final Structured Output
    # ----------------------------
    return {
        "nutrition_analysis": {
            "protein_coverage_percent": round(protein_percent, 2),
            "calorie_difference": round(calorie_difference, 2),
            "calorie_alignment_percent": round(calorie_alignment_percent, 2),
            "classification": {
                "protein": protein_class,
                "calories": calorie_class
            }
        },
        "score_breakdown": score_breakdown,
        "summary": summary
    }