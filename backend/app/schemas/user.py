from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    daily_calorie_target: float = Field(gt=0)
    daily_protein_target: float = Field(gt=0)
    allergies: Optional[str] = None
    weight_goal: Optional[float] = None
    current_weight: Optional[float] = None

class UserPreferencesUpdate(BaseModel):
    allergies: Optional[str] = None
    daily_calorie_target: Optional[float] = None
    weight_goal: Optional[float] = None
    current_weight: Optional[float] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
