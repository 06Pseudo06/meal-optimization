from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.auth_user import AuthUser
from app.auth.dependencies import get_current_user
from app.crud.log import calculate_today_macros
from app.models.daily_log import DailyLog
from app.models.recipe import Recipe

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    user = db.query(User).filter(User.auth_user_id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    # Macros
    totals = calculate_today_macros(db, user.id)
    cal_target = user.daily_calorie_target or 2000
    pro_target = user.daily_protein_target or 100
    carb_target = user.daily_carbs_target or 0
    fat_target = user.daily_fats_target or 0

    macros = {
        "calories_consumed": totals["total_calories"],
        "protein_consumed": totals["total_protein"],
        "carbs_consumed": totals["total_carbs"],
        "fats_consumed": totals["total_fats"],
        "calorie_target": cal_target,
        "protein_target": pro_target,
        "carbs_target": carb_target,
        "fats_target": fat_target
    }

    try:
        logs = db.query(DailyLog).filter(DailyLog.user_id == user.id).order_by(desc(DailyLog.consumed_at)).limit(5).all()
    except Exception as e:
        import logging
        logging.error(f"Failed to fetch logs: {e}")
        logs = []
    
    recent_intake = []
    for log in logs:
        recipe = db.query(Recipe).filter(Recipe.id == log.recipe_id).first()
        if recipe:
            dt = log.consumed_at if log.consumed_at else datetime.now()
            hour = dt.hour
            meal_type = 'Breakfast' if hour < 11 else 'Lunch' if hour < 15 else 'Snack' if hour < 18 else 'Dinner'
            recent_intake.append({
                "id": log.id,
                "name": recipe.name,
                "meal": meal_type,
                "time": dt.strftime("%I:%M %p"),
                "kcal": int(recipe.calories) if recipe.calories else 0,
                "tag": recipe.diet_type,
                "dots": ["#3838ff", "#ff6b6b"] if recipe.protein and recipe.protein > 20 else ["#2ed573"]
            })

    # Weight Journey
    weight_metrics = {
        "current_weight": user.current_weight,
        "weight_goal": user.weight_goal,
        "goal_delta": (user.current_weight - user.weight_goal) if (user.current_weight and user.weight_goal) else None
    }

    # Dynamic AI Insight
    adherence = totals["total_calories"] / cal_target if cal_target > 0 else 0
    pro_adherence = totals["total_protein"] / pro_target if pro_target > 0 else 0
    
    insight_quote = "Your tracking is looking solid today."
    insight_detail = "Keep logging your meals to get a more accurate picture of your nutrition."
    
    if adherence > 1.1:
        insight_quote = "You are currently tracking above your daily calorie goal."
        insight_detail = "Consider lighter, protein-rich options for your next meal to maintain balance."
    elif pro_adherence < 0.8 and adherence > 0.5:
        insight_quote = "You're slightly under your protein goal today."
        insight_detail = "Prioritize lean meats or plant-based protein in your next meal to support muscle recovery."
    elif adherence >= 0.8 and adherence <= 1.05 and pro_adherence >= 0.9:
        insight_quote = "Perfect alignment with your macro targets!"
        insight_detail = "Your protein and calorie pacing are exactly where they should be for optimal results."
    elif adherence < 0.3:
        insight_quote = "Let's get some meals logged!"
        insight_detail = "You have plenty of calories and macros remaining for the day. Make sure you fuel up."

    ai_insight = {
        "quote": insight_quote,
        "detail": insight_detail
    }

    return {
        "macros": macros,
        "recent_intake": recent_intake,
        "weight_metrics": weight_metrics,
        "ai_insight": ai_insight
    }
