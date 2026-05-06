import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
import re
import json
import logging

from app.models.recipe import Recipe
from app.ai.embedding_service import generate_offline_embeddings

def generate_slug(name: str) -> str:
    if not name: return ""
    slug = str(name).lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    return re.sub(r'[-\s]+', '-', slug).strip('-')

def normalize_text(text: str) -> str:
    if pd.isna(text) or not text: return None
    t = str(text).lower().strip()
    if t == "veg": return "vegetarian"
    if t in ["non veg", "non-veg"]: return "non_vegetarian"
    if t == "high protein": return "high_protein"
    return t

def seed_recipes(db: Session):
    BASE_DIR = Path(__file__).resolve().parents[2]
    csv_path = BASE_DIR / "data" / "recipes_master.csv"

    if not csv_path.exists():
        logging.warning("No recipes_master.csv found for seeding.")
        return

    df = pd.read_csv(csv_path)
    existing = {r.name for r in db.query(Recipe.name).all()}

    recipes = []

    for _, row in df.iterrows():
        name = row.get("name")
        if not name or name in existing:
            continue

        # Clamp health score
        raw_health_score = row.get("health_score")
        health_score = max(0.0, min(1.0, float(raw_health_score))) if pd.notna(raw_health_score) else None
        
        # Tags processing
        raw_tags = row.get("tags")
        tags = []
        if pd.notna(raw_tags):
            tags = [normalize_text(t) for t in str(raw_tags).split(",")]
            tags = [t for t in tags if t]
            
        slug = generate_slug(name)

        recipes.append(
            Recipe(
                name=name,
                slug=slug,
                calories=float(row.get("calories", 0)),
                protein=float(row.get("protein", 0)),
                diet_type=normalize_text(row.get("diet_type")),
                tags=tags,
                prep_time=int(row.get("prep_time")) if pd.notna(row.get("prep_time")) else None,
                difficulty=normalize_text(row.get("difficulty")),
                health_score=health_score,
                meal_type=normalize_text(row.get("meal_type")),
                cuisine=normalize_text(row.get("cuisine")),
                is_quick=bool(row.get("is_quick")) if pd.notna(row.get("is_quick")) else False,
                is_gym_friendly=bool(row.get("is_gym_friendly")) if pd.notna(row.get("is_gym_friendly")) else False,
                is_budget_friendly=bool(row.get("is_budget_friendly")) if pd.notna(row.get("is_budget_friendly")) else False,
                spice_level=normalize_text(row.get("spice_level")),
                description=str(row.get("description")) if pd.notna(row.get("description")) else None
            )
        )

    if recipes:
        db.bulk_save_objects(recipes)
        db.commit()
        logging.info(json.dumps({
            "event": "recipes_seeded",
            "count": len(recipes)
        }))
    else:
        logging.info("No new recipes to seed.")
        
    # Generate embeddings for any recipes that need it
    logging.info("Starting offline embedding generation...")
    generate_offline_embeddings(db)