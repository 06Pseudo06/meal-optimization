"""
scoring_config.py
-----------------
Central scoring configuration.
Defines weight importance for each feature.
No algorithmic logic here.
"""

SCORING_WEIGHTS = {
    "ingredient_match": 0.35,
    "protein_alignment": 0.25,
    "calorie_alignment": 0.20,
    "goal_tag_match": 0.15,
    "macro_density": 0.05,
}