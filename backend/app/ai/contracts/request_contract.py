"""
request_contract.py
Defines recommendation request format.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class RequestContract(BaseModel):
    calorie_max: Optional[float] = Field(default=None, gt=0)
    protein_min: Optional[float] = Field(default=None, gt=0)
    diet_type: Optional[str] = None
    ingredients: Optional[List[str]] = None
    goal: Optional[str] = None
    mood: Optional[str] = None
    time_of_day: Optional[str] = None