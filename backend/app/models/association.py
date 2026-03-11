from sqlalchemy import Column, Integer, ForeignKey, Float, String, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class RecipeIngredient(Base):

    __tablename__ = "recipe_ingredients"

    __table_args__ = (
        Index("idx_recipeingredient_recipe", "recipe_id"),
        Index("idx_recipeingredient_ingredient", "ingredient_id"),
    )

    recipe_id = Column(
        Integer,
        ForeignKey("recipes.id", ondelete="CASCADE"),
        primary_key=True
    )

    ingredient_id = Column(
        Integer,
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        primary_key=True
    )

    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)

    recipe = relationship(
        "Recipe",
        back_populates="ingredients"
    )

    ingredient = relationship(
        "Ingredient",
        back_populates="recipes"
    )