"""
user_contract.py
Defines user structure for AI engine.
"""

from pydantic import BaseModel
from typing import List


class UserContract(BaseModel):
    id: int
    daily_calorie_target: float
    daily_protein_target: float
    allergies: List[str] = []