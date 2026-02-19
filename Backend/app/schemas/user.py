from pydantic import BaseModel, Field

class UserBase(BaseModel):
    daily_calorie_target: float = Field(gt=0)
    daily_protein_target: float = Field(gt=0)

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
