import time
import json
import logging
from typing import List, Dict, Any, Optional

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
    # Initialize the model offline
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    logging.warning("Could not load SentenceTransformer: " + str(e))
    model = None

from app.models.recipe import Recipe

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

class VectorStoreRepository:
    """Abstract interface for vector storage to prepare for pgvector/FAISS"""
    def save_embedding(self, recipe_id: int, embedding: List[float], timestamp: int) -> bool:
        raise NotImplementedError
        
    def get_embedding(self, recipe_id: int) -> Optional[List[float]]:
        raise NotImplementedError

class JsonVectorStore(VectorStoreRepository):
    """Current implementation using JSON columns"""
    def __init__(self, db_session):
        self.db = db_session

    def save_embedding(self, recipe_id: int, embedding: List[float], timestamp: int) -> bool:
        recipe = self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            return False
            
        recipe.embedding = embedding
        recipe.embedding_model = EMBEDDING_MODEL_NAME
        recipe.embedding_dim = EMBEDDING_DIM
        recipe.embedding_timestamp = timestamp
        self.db.commit()
        return True

    def get_embedding(self, recipe_id: int) -> Optional[List[float]]:
        recipe = self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if recipe and recipe.embedding_model == EMBEDDING_MODEL_NAME:
            return recipe.embedding
        return None

def generate_recipe_text(recipe: Recipe) -> str:
    desc = getattr(recipe, "description", "") or ""
    cuisine = getattr(recipe, "cuisine", "") or ""
    tags_list = getattr(recipe, "tags", []) or []
    tags_str = ", ".join(tags_list) if isinstance(tags_list, list) else str(tags_list)
    meal_type = getattr(recipe, "meal_type", "") or ""
    difficulty = getattr(recipe, "difficulty", "") or ""
    
    # Extract ingredients name
    ingredients = []
    if hasattr(recipe, "ingredients"):
        for assoc in recipe.ingredients:
            if assoc.ingredient:
                ingredients.append(assoc.ingredient.name)
    ing_str = ", ".join(ingredients)
    
    return f"{recipe.name}. {desc}. Ingredients: {ing_str}. Cuisine: {cuisine}. Tags: {tags_str}. Type: {meal_type}. Difficulty: {difficulty}.".strip()

def generate_offline_embeddings(db) -> dict:
    """Batch generate embeddings offline (e.g. during seeding)."""
    if not model:
        return {"status": "error", "message": "Model not loaded"}

    recipes = db.query(Recipe).all()
    store = JsonVectorStore(db)
    
    generated = 0
    skipped = 0
    
    current_time = int(time.time())
    
    for recipe in recipes:
        # Check staleness
        recipe_updated = getattr(recipe, "updated_at", 0) or 0
        emb_timestamp = getattr(recipe, "embedding_timestamp", 0) or 0
        
        # Regenerate if metadata changed or model is missing/different
        needs_regeneration = (
            recipe_updated > emb_timestamp or
            recipe.embedding_model != EMBEDDING_MODEL_NAME or
            not recipe.embedding
        )
        
        if needs_regeneration:
            try:
                logging.info(json.dumps({"event": "embedding_generation_started", "recipe_id": recipe.id}))
                text = generate_recipe_text(recipe)
                emb = model.encode(text).tolist()
                store.save_embedding(recipe.id, emb, current_time)
                generated += 1
                logging.info(json.dumps({"event": "embedding_generated", "recipe_id": recipe.id}))
            except Exception as e:
                logging.error(json.dumps({"event": "embedding_failed", "recipe_id": recipe.id, "error": str(e)}))
        else:
            skipped += 1
            
    logging.info(json.dumps({
        "event": "offline_embedding_batch_complete",
        "generated": generated,
        "skipped": skipped
    }))
    
    return {
        "generated": generated,
        "skipped": skipped,
        "status": "success"
    }

# LRU cache for query embeddings to avoid re-embedding identical queries
_QUERY_CACHE = {}

def get_query_embedding(query: str) -> Optional[List[float]]:
    """Generate embedding for a user query live."""
    if not query or not str(query).strip():
        return None
    
    if not model:
        return None
        
    query_key = query.lower().strip()
    if query_key in _QUERY_CACHE:
        return _QUERY_CACHE[query_key]
        
    try:
        emb = model.encode(query_key).tolist()
        if len(_QUERY_CACHE) > 1000:
            _QUERY_CACHE.pop(next(iter(_QUERY_CACHE)))
        _QUERY_CACHE[query_key] = emb
        return emb
    except Exception as e:
        logging.error(json.dumps({"event": "query_embedding_failed", "error": str(e)}))
        return None
