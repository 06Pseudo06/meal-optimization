from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.recommendation import RecommendationRequest
from app.services.recommendation_service import recommend_recipes

router = APIRouter(prefix="/recipes", tags=["Recommendations"])


@router.post("/recommend")
def recommend(request: RecommendationRequest, db: Session = Depends(get_db)):
    return recommend_recipes(db, request)
