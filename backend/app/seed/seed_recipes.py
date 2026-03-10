import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session

from app.models.recipe import Recipe


def seed_recipes(db: Session):

    BASE_DIR = Path(__file__).resolve().parents[2]
    csv_path = BASE_DIR / "data" / "recipes_master.csv"

    df = pd.read_csv(csv_path)

    existing = {r.name for r in db.query(Recipe.name).all()}

    recipes = []

    for _, row in df.iterrows():

        if row["name"] in existing:
            continue

        recipes.append(
            Recipe(
                name=row["name"],
                calories=row["calories"],
                protein=row["protein"],
                diet_type=row["diet_type"],
                tags=row["tags"]
            )
        )

    db.bulk_save_objects(recipes)
    db.commit()

    print(f"Recipes seeded: {len(recipes)}")