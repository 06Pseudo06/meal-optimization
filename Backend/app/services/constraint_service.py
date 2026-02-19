from sqlalchemy.orm import Session
from app.models.recipe import Recipe


def apply_constraints(db: Session, request):

    query = db.query(Recipe)

    if request.calorie_max:
        query = query.filter(Recipe.calories <= request.calorie_max)

    if request.protein_min:
        query = query.filter(Recipe.protein >= request.protein_min)

    if request.diet_type:
        query = query.filter(Recipe.diet_type == request.diet_type)

    return query.all()
