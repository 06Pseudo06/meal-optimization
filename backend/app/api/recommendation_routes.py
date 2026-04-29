from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.recommendation import RecommendationRequest, RecommendationResponseItem, RecommendationResponse
from app.services.recommendation_service import recommend_recipes

from app.auth.dependencies import get_current_user, get_current_user_optional
from app.models.auth_user import AuthUser
from app.models.user import User


router = APIRouter(prefix="/recipes", tags=["Recommendations"])


@router.post("/recommend", response_model=RecommendationResponse)
def recommend(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user_optional)
):
    print("REQUEST RECEIVED:", request.model_dump())

    if current_user:
        user = db.query(User).filter(User.auth_user_id == current_user.id).first()
    else:
        # Fallback to testing mode
        user = db.query(User).first()
        if not user:
            raise HTTPException(status_code=401, detail="Testing mode failed: No user found. Please authenticate.")

    from app.core.exceptions import ProfileNotFoundException

    if not user:
        raise ProfileNotFoundException()

    results = recommend_recipes(db, request, user.id)
    return results

import json
from app.models.recommendation_log import RecommendationLog
from app.models.recipe import Recipe

@router.get("/history")
def get_recommendation_history(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    user = db.query(User).filter(User.auth_user_id == current_user.id).first()
    from app.core.exceptions import ProfileNotFoundException
    if not user:
        raise ProfileNotFoundException()
    
    logs = db.query(RecommendationLog).filter(RecommendationLog.user_id == user.id).order_by(RecommendationLog.created_at.desc()).all()
    
    history = []
    for log in logs:
        try:
            recipe_ids = json.loads(log.recommended_recipe_ids)
            recipes = db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
            history.append({
                "id": log.id,
                "requested_ingredients": json.loads(log.ingredients) if log.ingredients else [],
                "created_at": log.created_at,
                "recommendations": recipes
            })
        except:
            continue
            
    return history