from pydantic import BaseModel
from datetime import datetime

class DailyLogCreate(BaseModel):
    user_id: int
    recipe_id: int

class DailyLogResponse(BaseModel):
    id: int
    user_id: int
    recipe_id: int
    consumed_at: datetime

    class Config:
        from_attributes = True
