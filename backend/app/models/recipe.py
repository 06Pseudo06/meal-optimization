from sqlalchemy import Column, Integer, String, Float, Index, JSON, BigInteger, Boolean, CheckConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import time

class Recipe(Base):
    __tablename__ = "recipes"

    __table_args__ = (
        Index("idx_recipe_diet", "diet_type"),
        CheckConstraint("health_score >= 0 AND health_score <= 1", name="ck_recipe_health_score"),
        CheckConstraint("prep_time >= 0", name="ck_recipe_prep_time")
    )

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    carbs = Column(Float, nullable=True)
    fats = Column(Float, nullable=True)

    diet_type = Column(String, nullable=False)
    
    # Semantic Fields
    prep_time = Column(Integer, nullable=True)
    difficulty = Column(String, nullable=True)
    health_score = Column(Float, nullable=True)
    meal_type = Column(String, nullable=True)
    cuisine = Column(String, nullable=True)
    protein_density = Column(Float, nullable=True)
    calorie_density = Column(Float, nullable=True)
    is_quick = Column(Boolean, server_default=text('false'))
    is_gym_friendly = Column(Boolean, server_default=text('false'))
    is_budget_friendly = Column(Boolean, server_default=text('false'))
    spice_level = Column(String, nullable=True)

    tags = Column(JSONB, nullable=True)
    embedding = Column(JSON, nullable=True) # Keeping JSON per user requirement
    embedding_model = Column(String, nullable=True)
    embedding_dim = Column(Integer, nullable=True)
    embedding_timestamp = Column(BigInteger, server_default=text("0"))
    
    created_at = Column(BigInteger, default=lambda: int(time.time()), server_default="0", nullable=False)
    updated_at = Column(BigInteger, default=lambda: int(time.time()), onupdate=lambda: int(time.time()), server_default="0", nullable=False)

    ingredients = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete"
    )

    logs = relationship(
        "DailyLog",
        back_populates="recipe"
    ) 