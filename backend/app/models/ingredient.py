from sqlalchemy import Column, Integer, String, Float, Boolean, BigInteger, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import time

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    
    category = Column(String, nullable=True)
    aliases = Column(JSONB, nullable=True)
    protein_per_100g = Column(Float, nullable=True)
    calories_per_100g = Column(Float, nullable=True)
    is_allergen = Column(Boolean, server_default=text('false'))
    
    created_at = Column(BigInteger, default=lambda: int(time.time()), server_default="0", nullable=False)
    updated_at = Column(BigInteger, default=lambda: int(time.time()), onupdate=lambda: int(time.time()), server_default="0", nullable=False)

    recipes = relationship(
        "RecipeIngredient",
        back_populates="ingredient",
        cascade="all, delete"
    )
