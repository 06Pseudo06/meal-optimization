from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.daily_log import DailyLogCreate, DailyLogResponse
from app.crud.log import add_log, get_today_logs, calculate_today_macros
from app.models.user import User

router = APIRouter(prefix="/logs", tags=["Daily Logs"])

@router.post("/", response_model=DailyLogResponse)
def create_log(log: DailyLogCreate, db: Session = Depends(get_db)):
    return add_log(db, log.user_id, log.recipe_id)

@router.get("/today/{user_id}")
def get_today_summary(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    totals = calculate_today_macros(db, user_id)

    return {
        "calories_consumed": totals["total_calories"],
        "protein_consumed": totals["total_protein"],
        "calorie_target": user.daily_calorie_target,
        "protein_target": user.daily_protein_target,
        "remaining_calories": user.daily_calorie_target - totals["total_calories"],
        "remaining_protein": user.daily_protein_target - totals["total_protein"]
    }
