import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
import logging
import json

from app.models.ingredient import Ingredient

def seed_ingredients(db: Session):
    BASE_DIR = Path(__file__).resolve().parents[2]
    csv_path = BASE_DIR / "data" / "recipes.csv"

    if not csv_path.exists():
        logging.warning("No recipes.csv found for ingredient seeding.")
        return

    df = pd.read_csv(csv_path)

    csv_ingredients = set(df["name-2"].dropna().unique())
    existing = {i.name for i in db.query(Ingredient.name).all()}
    new_ingredients = csv_ingredients - existing

    ingredients = []
    for name in new_ingredients:
        ingredients.append(
            Ingredient(
                name=name,
                category=None,
                aliases=[],
                is_allergen=False
            )
        )

    if ingredients:
        db.bulk_save_objects(ingredients)
        db.commit()
        logging.info(json.dumps({
            "event": "ingredients_seeded",
            "count": len(ingredients)
        }))
    else:
        logging.info("No new ingredients to seed.")