from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 

from app.core.database import get_db
from app.models.recipe import Recipe
from app.schemas.recipes import RecipeCreate, RecipeUpdate, RecipeOut
from app.schemas.recipes import RecipePagination
from app.crud import recipes as crud_recipe

from app.auth.dependencies import get_current_user
from app.models.auth_user import AuthUser


router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.get("/", response_model=RecipePagination)
def get_recipes(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
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

 
@router.get("/{recipe_id}", response_model=RecipeOut)
def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):

    recipe = crud_recipe.get_recipe(db, recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe

 
@router.post("/", response_model=RecipeOut)
def create_recipe(
    recipe: RecipeCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):

    return crud_recipe.create_recipe(db, recipe)

 
@router.put("/{recipe_id}", response_model=RecipeOut)
def update_recipe(
    recipe_id: int,
    recipe: RecipeUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):

    updated = crud_recipe.update_recipe(db, recipe_id, recipe)

    if not updated:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return updated


 
@router.delete("/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):

    deleted = crud_recipe.delete_recipe(db, recipe_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {"message": "Recipe deleted successfully"}

