from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.recipe import Recipe
from app.schemas.recipes import RecipeCreate, RecipeUpdate, RecipeOut, RecipeBase
from app.crud import recipes as crud_recipe
from app.schemas.recipes import RecipePagination

router = APIRouter(prefix="/recipes", tags=["Recipes"])

@router.get("/", response_model=RecipePagination)
def get_recipes(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    limit = min(limit, 100)

    recipes = db.query(Recipe).offset(offset).limit(limit).all()
    total = db.query(Recipe).count()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": recipes
    }



@router.get("/", response_model=RecipePagination)
def get_recipes(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    limit = min(limit, 100)

    recipes = db.query(Recipe).offset(offset).limit(limit).all()
    total = db.query(Recipe).count()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": recipes,
        "data": recipes
    }


@router.get("/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = crud_recipe.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.post("/", response_model=RecipeOut)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    return crud_recipe.create_recipe(db, recipe)


@router.put("/{recipe_id}", response_model=RecipeOut)
def update_recipe(recipe_id: int, recipe: RecipeUpdate, db: Session = Depends(get_db)):
    updated = crud_recipe.update_recipe(db, recipe_id, recipe)
    if not updated:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return updated


@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    deleted = crud_recipe.delete_recipe(db, recipe_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"message": "Recipe deleted successfully"}