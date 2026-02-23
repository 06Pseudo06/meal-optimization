"""
validator.py
Input safety layer for AI engine.
Ensures clean structured input before processing.
"""

from typing import List
from AI.contracts.recipe_contract import RecipeContract
from AI.contracts.request_contract import RequestContract


class ValidationError(Exception):
    """Custom validation exception."""
    pass


def validate_request(request: RequestContract) -> None:
    """
    Validates request contract.
    """

    # Example: calorie & protein must be positive if provided
    if request.calorie_max is not None and request.calorie_max <= 0:
        raise ValidationError("calorie_max must be positive.")

    if request.protein_min is not None and request.protein_min <= 0:
        raise ValidationError("protein_min must be positive.")

    # Ingredients must be list if provided
    if request.ingredients is not None and not isinstance(request.ingredients, list):
        raise ValidationError("ingredients must be a list.")

    # No malformed strings
    if request.diet_type is not None and not isinstance(request.diet_type, str):
        raise ValidationError("diet_type must be a string.")


def validate_recipes(recipes: List[RecipeContract]) -> None:
    """
    Validates recipe list before engine processing.
    """

    if not isinstance(recipes, list):
        raise ValidationError("recipes must be a list.")

    for recipe in recipes:

        if recipe.id is None:
            raise ValidationError("Recipe ID missing.")

        if not isinstance(recipe.calories, (int, float)):
            raise ValidationError(f"Invalid calories for recipe {recipe.name}")

        if not isinstance(recipe.protein, (int, float)):
            raise ValidationError(f"Invalid protein value for recipe {recipe.name}")

        if recipe.calories < 0 or recipe.protein < 0:
            raise ValidationError(f"Negative macro value in recipe {recipe.name}")