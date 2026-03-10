import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session

from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.association import RecipeIngredient


def seed_mappings(db: Session):

    BASE_DIR = Path(__file__).resolve().parents[2]
    csv_path = BASE_DIR / "data" / "recipes.csv"

    df = pd.read_csv(csv_path)

    recipe_map = {r.name: r.id for r in db.query(Recipe).all()}
    ingredient_map = {i.name: i.id for i in db.query(Ingredient).all()}

    existing_pairs = {
        (m.recipe_id, m.ingredient_id)
        for m in db.query(
            RecipeIngredient.recipe_id,
            RecipeIngredient.ingredient_id
        ).all()
    }

    mappings = []

    for _, row in df.iterrows():

        recipe_id = recipe_map.get(row["name"])
        ingredient_id = ingredient_map.get(row["name-2"])

        if not recipe_id or not ingredient_id:
            continue

        pair = (recipe_id, ingredient_id)

        if pair in existing_pairs:
            continue

        mappings.append(
            RecipeIngredient(
                recipe_id=recipe_id,
                ingredient_id=ingredient_id,
                quantity=float(row["quantity"]),
                unit=row["unit"]
            )
        )

    db.bulk_save_objects(mappings)
    db.commit()

    print(f"Mappings seeded: {len(mappings)}")