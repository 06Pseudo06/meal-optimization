from sqlalchemy import Column, Integer, String, Float, Index, JSON, BigInteger
from sqlalchemy.orm import relationship
from app.core.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    __table_args__ = (
        Index("idx_recipe_diet", "diet_type"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    carbs = Column(Float, nullable=True)
    fats = Column(Float, nullable=True)

    diet_type = Column(String, nullable=False)
    tags = Column(String)
    embedding = Column(JSON, nullable=True)
    updated_at = Column(BigInteger, default=0)

    ingredients = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete"
    )

    logs = relationship(
        "DailyLog",
        back_populates="recipe"
    ) 