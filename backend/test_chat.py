import sys
import os
import json

# Setup path so we can import from app
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.recommendation_service import get_recommendations, USER_MEMORY
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.core.database import Base
from app.models.recipe import Recipe
from app.models.user_profile import UserProfile
from app.models.user_history import UserHistory

# Mock DB Session
from unittest.mock import MagicMock

class MockDB:
    def __init__(self):
        self.recipes = [
            Recipe(id=1, name="Egg Curry", calories=400, protein=30, diet_type="non-veg"),
            Recipe(id=2, name="Chicken Salad", calories=500, protein=40, diet_type="non-veg"),
            Recipe(id=3, name="Veg Bowl", calories=300, protein=15, diet_type="veg"),
            Recipe(id=4, name="High Protein Tofu", calories=350, protein=35, diet_type="veg")
        ]
        self.profile = UserProfile(user_id=1, preferred_ingredients={})
        self.history = []

    def query(self, model):
        mock_query = MagicMock()
        if model == Recipe:
            mock_query.limit.return_value.all.return_value = self.recipes
            mock_query.options.return_value.all.return_value = self.recipes
            mock_query.all.return_value = self.recipes
        elif model == UserProfile:
            mock_query.filter.return_value.first.return_value = self.profile
        elif model == UserHistory:
            mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = self.history
        return mock_query

    def add(self, item):
        pass

    def commit(self):
        pass
        
    def refresh(self, item):
        pass

db = MockDB()

class UserInput:
    def __init__(self, query):
        self.query = query
        self.user_id = 1

def run_test(query, test_name):
    print(f"\n--- Testing: {test_name} ('{query}') ---")
    res = get_recommendations(UserInput(query), db)
    if "message" in res:
        print(f"MESSAGE: {res['message']}")
    else:
        print(f"RECIPES: {[r.get('recipe', {}).get('name') for r in res.get('data', [])]}")
        print(f"META: {res.get('meta')}")

# Clear memory first
USER_MEMORY.clear()

run_test("hi", "hi -> clarification, no recipe")
run_test("high protein meal", "high protein meal -> protein-based result")
run_test("eggs", "eggs -> egg recipe")
run_test("veg", "veg -> veg only")
run_test("chicken", "chicken -> chicken recipe")
run_test("high protein", "high protein after chicken -> not forced chicken")

