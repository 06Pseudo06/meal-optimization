import os
import pandas as pd
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.recipe import Recipe


def seed_recipes():

    db: Session = SessionLocal()

    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(base_dir, "data", "recipes_master.csv")

        df = pd.read_csv(csv_path)

        for _, row in df.iterrows():

            # Prevent duplicate insert
            existing = db.query(Recipe).filter(
                Recipe.name == row["name"]
            ).first()

            if existing:
                continue

            recipe = Recipe(
                name=row["name"],
                calories=row["calories"],
                protein=row["protein"],
                diet_type=row["diet_type"],
                tags=row["tags"]
            )

            db.add(recipe)

        db.commit()
        print("✅ Recipes seeded successfully.")

    except Exception as e:
        db.rollback()
        print("❌ Error seeding recipes:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_recipes()
