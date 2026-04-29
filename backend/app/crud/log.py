from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.models.daily_log import DailyLog
from app.models.recipe import Recipe

def add_log(db: Session, user_id: int, recipe_id: int):
    log = DailyLog(user_id=user_id, recipe_id=recipe_id)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_today_logs(db: Session, user_id: int):
    today = date.today()

    return (
        db.query(DailyLog)
        .filter(
            DailyLog.user_id == user_id,
            func.date(DailyLog.consumed_at) == today
        )
        .all()
    )

def calculate_today_macros(db: Session, user_id: int):
    today = date.today()

    result = (
        db.query(
            func.sum(Recipe.calories),
            func.sum(Recipe.protein),
            func.sum(Recipe.carbs),
            func.sum(Recipe.fats)
        )
        .join(DailyLog, DailyLog.recipe_id == Recipe.id)
        .filter(
            DailyLog.user_id == user_id,
            func.date(DailyLog.consumed_at) == today
        )
        .first()
    )

    calories = result[0] or 0
    protein = result[1] or 0
    carbs = result[2] or 0
    fats = result[3] or 0

    return {
        "total_calories": calories,
        "total_protein": protein,
        "total_carbs": carbs,
        "total_fats": fats
    }
