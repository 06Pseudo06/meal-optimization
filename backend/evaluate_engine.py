import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.recommendation_service import get_recommendations, USER_MEMORY
from app.models.recipe import Recipe
from app.models.user_profile import UserProfile
from app.models.user_history import UserHistory
from unittest.mock import MagicMock

class MockDB:
    def __init__(self):
        self.recipes = [
            Recipe(id=1, name="Egg Curry", calories=400, protein=30, diet_type="non-veg"),
            Recipe(id=2, name="Chicken Salad", calories=500, protein=40, diet_type="non-veg"),
            Recipe(id=3, name="Veg Bowl", calories=300, protein=15, diet_type="veg"),
            Recipe(id=4, name="High Protein Tofu", calories=350, protein=35, diet_type="veg"),
            Recipe(id=5, name="Low Calorie Salad", calories=250, protein=10, diet_type="veg"),
            Recipe(id=6, name="Healthy Quinoa", calories=350, protein=12, diet_type="veg"),
            Recipe(id=7, name="Quick Chicken Dinner", calories=450, protein=35, diet_type="non-veg", difficulty="easy", is_quick=True)
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

    def add(self, item): pass
    def commit(self): pass
    def refresh(self, item): pass

db = MockDB()

class UserInput:
    def __init__(self, query):
        self.query = query
        self.user_id = 1

def run_test(query, test_name):
    print(f"\n--- Testing: {test_name} ('{query}') ---")
    USER_MEMORY.clear() # clear memory to test raw queries
    res = get_recommendations(UserInput(query), db)
    
    if "message" in res:
        print(f"MESSAGE: {res['message']}")
    else:
        print(f"RECIPES: {[r.get('recipe', {}).get('name') for r in res.get('data', [])]}")
        
    print(f"META REASON: {res.get('meta', {}).get('reason')}")
    if res.get('data') and 'confidence' in res['data'][0]:
        print(f"TOP CONFIDENCE: {res['data'][0]['confidence']}")

def run_all_tests():
    print("====================================")
    print("     EVALUATE ENGINE HARNESS")
    print("====================================")
    
    # 1. Greeting Flow
    print("\n[Greeting Flow]")
    run_test("hi", "Greeting - hi")
    run_test("hello", "Greeting - hello")
    run_test("hey", "Greeting - hey")

    # 2. Ingredient Queries
    print("\n[Ingredient Queries]")
    run_test("chicken recipe", "Ingredient - chicken")
    run_test("something with tofu", "Ingredient - tofu")
    run_test("egg breakfast", "Ingredient - egg")

    # 3. Semantic Queries
    print("\n[Semantic Queries]")
    run_test("low calorie meal", "Semantic - low calorie")
    run_test("healthy dinner", "Semantic - healthy")
    run_test("gym meal", "Semantic - gym")

    # 4. Mixed Queries
    print("\n[Mixed Queries]")
    run_test("high protein veg meal", "Mixed - high protein veg")
    run_test("quick chicken dinner", "Mixed - quick chicken")

    # 5. Typo Queries
    print("\n[Typo Queries]")
    run_test("high protien", "Typo - protien")
    run_test("low cslorie", "Typo - cslorie")
    
    # 6. Gemini Offline Mode
    print("\n[Gemini Offline Mode]")
    import app.ai.intent_parser
    original_llm = app.ai.intent_parser.generate_llm_response
    
    def offline_llm(*args, **kwargs):
        raise Exception("Simulated Gemini Quota Failure")
        
    app.ai.intent_parser.generate_llm_response = offline_llm
    try:
        run_test("high protein chicken meal", "Offline - high protein chicken")
        run_test("low calorie vegetarian", "Offline - low calorie veg")
    finally:
        app.ai.intent_parser.generate_llm_response = original_llm

if __name__ == "__main__":
    run_all_tests()
