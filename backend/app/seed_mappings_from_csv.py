import pandas as pd
from app.core.database import SessionLocal
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.association import RecipeIngredient
from pathlib import Path


def seed_mappings():

    db = SessionLocal() 
    BASE_DIR = Path(__file__).resolve().parent.parent
    csv_path = BASE_DIR / "data" / "recipes.csv"


    ingredient_cache = {}

    df = pd.read_csv(csv_path)

    for _, row in df.iterrows():

        recipe_name = row["name"]
        ingredient_name = row["name-2"]
        quantity = float(row["quantity"])
        unit = row["unit"]

        recipe = db.query(Recipe).filter_by(name=recipe_name).first()

        if not recipe:
            print(f"Recipe not found: {recipe_name}")
            continue

        if ingredient_name not in ingredient_cache:
            ingredient = db.query(Ingredient).filter_by(name=ingredient_name).first()
            if not ingredient:
                ingredient = Ingredient(name=ingredient_name)
                db.add(ingredient)
                db.flush()
            ingredient_cache[ingredient_name] = ingredient

        ingredient_obj = ingredient_cache[ingredient_name]

        mapping = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ingredient_obj.id,
            quantity=quantity,
            unit=unit
        )

        db.add(mapping)

    db.commit()
    db.close()

    print("Mappings seeded.")

if __name__ == "__main__":
    seed_mappings()

