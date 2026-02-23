"""
user_contract.py
Defines user structure for AI engine.
"""

from typing import Optional
from pydantic import BaseModel


class UserContract(BaseModel):
    user_id: Optional[int] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    activity_level: Optional[str] = None
    goal: Optional[str] = None