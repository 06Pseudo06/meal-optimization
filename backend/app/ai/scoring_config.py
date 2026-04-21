"""
scoring_config.py
-----------------
Central scoring configuration.
Defines weight importance for each feature.
No algorithmic logic here.
"""

SCORING_WEIGHTS = {
    "ingredient_match": 0.15,
    "protein_alignment": 0.30,
    "calorie_alignment": 0.30,
    "goal_tag_match": 0.10,
    "macro_density": 0.15,
    "carb_ratio": 0.05,
    "fat_ratio": 0.05,
}