import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session

from app.models.ingredient import Ingredient


def seed_ingredients(db: Session):

    BASE_DIR = Path(__file__).resolve().parents[2]
    csv_path = BASE_DIR / "data" / "recipes.csv"

    df = pd.read_csv(csv_path)

    csv_ingredients = set(df["name-2"].dropna().unique())

    existing = {i.name for i in db.query(Ingredient.name).all()}

    new_ingredients = csv_ingredients - existing

    ingredients = [
        Ingredient(name=name) for name in new_ingredients
    ]

    db.bulk_save_objects(ingredients)
    db.commit()

    print(f"Ingredients seeded: {len(ingredients)}")