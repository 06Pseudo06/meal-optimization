from pydantic import BaseModel, Field
from typing import List, Optional


class RecommendationRequest(BaseModel):

    calorie_max: Optional[float] = Field(
        default=None,
        gt=0,
        description="Maximum allowed calories"
    )

    protein_min: Optional[float] = Field(
        default=None,
        ge=0,
        description="Minimum required protein"
    )

    diet_type: Optional[str] = Field(
        default=None,
        description="Diet preference (veg / non-veg)"
    )

    ingredients: Optional[List[str]] = Field(
        default=None,
        description="List of available ingredients"
    )

    goal: Optional[str] = Field(
        default=None,
        description="User goal (bulk, cut, light, comfort, etc.)"
    )

    mood: Optional[str] = Field(
        default=None,
        description="User mood preference"
    )

    time_of_day: Optional[str] = Field(
        default=None,
        description="Breakfast, lunch, dinner, snack"
    )

    query: Optional[str] = Field(
    default=None,
    description="Natural language meal request"
    )

class RecipeInfo(BaseModel):
    id: int
    name: str
    calories: Optional[float] = 0.0
    protein: Optional[float] = 0.0

class RecommendationExplanation(BaseModel):
    ingredient_alignment: float = 0.0
    protein_alignment: float = 0.0
    calorie_alignment: float = 0.0

class RecommendationResponseItem(BaseModel):
    recipe: RecipeInfo
    score: float = 0.0
    explanation: RecommendationExplanation