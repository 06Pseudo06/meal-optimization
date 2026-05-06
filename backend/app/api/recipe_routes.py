from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session 
import logging
import json 

from app.core.database import get_db
from app.models.recipe import Recipe
from app.schemas.recipes import RecipeCreate, RecipeUpdate, RecipeOut
from app.schemas.recipes import RecipePagination
from app.crud import recipes as crud_recipe

from app.auth.dependencies import get_current_user
from app.models.auth_user import AuthUser


router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.get("/search")
def search_recipes(
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1),
    db: Session = Depends(get_db)
):
    try:
        q_lower = q.lower().strip()
        print("SEARCH QUERY:", q_lower)
        logging.info(json.dumps({"event": "search_recipes_started", "query": q_lower}))
        
        # 1. Fuzzy match
        recipes = db.query(Recipe).filter(Recipe.name.ilike(f"%{q_lower}%")).limit(limit).all()
        logging.info(json.dumps({"event": "search_fuzzy_match", "count": len(recipes)}))
        
        if not recipes:
            # 2. Semantic fallback
            from app.ai.embedding_service import get_query_embedding
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
            
            logging.info(json.dumps({"event": "search_semantic_fallback_triggered"}))
            q_emb = get_query_embedding(q_lower)
            if q_emb:
                all_recipes = db.query(Recipe).all()
                scored = []
                for r in all_recipes:
                    if r.embedding:
                        score = cosine_similarity(np.array([q_emb]), np.array([r.embedding]))[0][0]
                        scored.append((r, score))
                scored.sort(key=lambda x: x[1], reverse=True)
                recipes = [x[0] for x in scored[:limit]]
                logging.info(json.dumps({"event": "search_semantic_success", "count": len(recipes)}))
                
        # Manually construct response to avoid Pydantic serialization mismatches entirely
        final_recipes = []
        if recipes:
            for r in recipes:
                final_recipes.append({
                    "id": r.id,
                    "name": r.name,
                    "calories": float(r.calories) if r.calories is not None else 0.0,
                    "protein": float(r.protein) if r.protein is not None else 0.0,
                    "carbs": float(r.carbs) if r.carbs is not None else None,
                    "fats": float(r.fats) if r.fats is not None else None,
                    "diet_type": r.diet_type,
                    "tags": r.tags
                })
        
        logging.info(json.dumps({"event": "search_recipes_completed", "final_count": len(final_recipes)}))
        return {"recipes": final_recipes}
    except Exception as e:
        logging.error(json.dumps({"event": "search_recipes_error", "error": str(e)}))
        return {"recipes": []}


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
