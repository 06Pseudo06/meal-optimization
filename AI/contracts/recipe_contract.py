"""
recipe_contract.py
Defines recipe structure for AI engine.
"""

from typing import List, Optional
from pydantic import BaseModel


class RecipeContract(BaseModel):
    id: int
    name: str
    calories: float
    protein: float
    carbs: Optional[float] = 0.0
    fats: Optional[float] = 0.0
    diet_type: str
    ingredients: Optional[List[str]] = []
    tags: Optional[str] = ""