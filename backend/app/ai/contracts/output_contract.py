"""
output_contract.py
Defines final recommendation response structure.
"""

from typing import List, Dict
from pydantic import BaseModel


class FeatureBreakdown(BaseModel):
    ingredient_match: float
    protein_alignment: float
    calorie_alignment: float
    goal_tag_match: float
    macro_density: float


class RecommendationOutput(BaseModel):
    id: int
    name: str
    calories: float
    protein: float
    score: float
    explanation: FeatureBreakdown