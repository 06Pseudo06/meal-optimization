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
        gt=0,
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
