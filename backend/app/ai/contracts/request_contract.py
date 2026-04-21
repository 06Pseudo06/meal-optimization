"""
request_contract.py
Defines recommendation request format.
"""

from typing import Optional, List
from pydantic import BaseModel


class RequestContract(BaseModel):
    calorie_max: Optional[float] = None
    protein_min: Optional[float] = None

    diet_type: Optional[str] = None
    ingredients: Optional[List[str]] = None
    exclude_ingredients: Optional[List[str]] = []

    goal: Optional[str] = None
    mood: Optional[str] = None
    time_of_day: Optional[str] = None

    quick_meal: Optional[bool] = False
    budget: Optional[str] = None