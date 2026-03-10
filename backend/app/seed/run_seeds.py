from app.core.database import SessionLocal

from app.seed.seed_recipes import seed_recipes
from app.seed.seed_ingredients import seed_ingredients
from app.seed.seed_mappings import seed_mappings


def run():

    db = SessionLocal()

    try:

        print("Starting database seeding...")

        seed_recipes(db)
        seed_ingredients(db)
        seed_mappings(db)

        print("Database seeding completed.")

    finally:
        db.close()


if __name__ == "__main__":
    run()