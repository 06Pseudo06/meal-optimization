from pydantic import BaseModel
from typing import Optional



class RecipeBase(BaseModel):
    id: int
    name: str
    calories: float
    protein: float
    carbs: Optional[float] = None
    fats: Optional[float] = None
    diet_type: Optional[str] = None
    tags: Optional[str] = None


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fats: Optional[float] = None
    diet_type: Optional[str] = None
    tags: Optional[str] = None


class RecipeOut(RecipeBase):
    id: int

    class Config:
        from_attributes = True