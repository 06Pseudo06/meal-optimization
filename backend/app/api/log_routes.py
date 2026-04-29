from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.daily_log import DailyLogCreate, DailyLogResponse
from app.crud.log import add_log, calculate_today_macros
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.models.auth_user import AuthUser


router = APIRouter(
    prefix="/logs",
    tags=["Daily Logs"]
)


@router.post("/", response_model=DailyLogResponse)
def create_log(
    log: DailyLogCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):

    user = db.query(User).filter(User.auth_user_id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    return add_log(db, user.id, log.recipe_id)



@router.get("/today")
def get_today_summary(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):

    user = db.query(User).filter(User.auth_user_id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    totals = calculate_today_macros(db, user.id)

    carbs_target = user.daily_carbs_target or 0
    fats_target = user.daily_fats_target or 0

    return {
        "calories_consumed": totals["total_calories"],
        "protein_consumed": totals["total_protein"],
        "carbs_consumed": totals["total_carbs"],
        "fats_consumed": totals["total_fats"],
        "calorie_target": user.daily_calorie_target,
        "protein_target": user.daily_protein_target,
        "carbs_target": carbs_target,
        "fats_target": fats_target,
        "remaining_calories": user.daily_calorie_target - totals["total_calories"],
        "remaining_protein": user.daily_protein_target - totals["total_protein"],
        "remaining_carbs": carbs_target - totals["total_carbs"] if carbs_target > 0 else 0,
        "remaining_fats": fats_target - totals["total_fats"] if fats_target > 0 else 0
    } 