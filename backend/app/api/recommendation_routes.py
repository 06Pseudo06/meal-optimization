from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.recommendation import RecommendationRequest
from app.services.recommendation_service import recommend_recipes

from app.auth.dependencies import get_current_user
from app.models.auth_user import AuthUser
from app.models.user import User


router = APIRouter(prefix="/recipes", tags=["Recommendations"])


@router.post("/recommend")
def recommend(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):

    
    user = db.query(User).filter(User.auth_user_id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    return recommend_recipes(db, request, user.id)