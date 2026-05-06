import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

import json
from app.core.database import SessionLocal
from app.ai.engine import RecommendationEngine

TEST_CASES = [
    {
        "query": "I want a high protein chicken meal",
        "expected_diet": None,
        "expected_health": None,
        "must_include": "chicken",
        "expected_protein_high": True
    },
    {
        "query": "A quick and easy paneer dish",
        "expected_diet": "veg",
        "expected_health": None,
        "must_include": "paneer",
        "expected_difficulty_easy": True
    },
    {
        "query": "something healthy and low calorie",
        "expected_diet": None,
        "expected_health": True,
        "expected_calorie_low": True
    }
]

def run_evaluation():
    db = SessionLocal()
    engine = RecommendationEngine()
    
    total = len(TEST_CASES)
    passed = 0
    
    print("\n--- Starting Evaluation Harness ---\n")
    
    for idx, case in enumerate(TEST_CASES):
        print(f"Test {idx+1}: '{case['query']}'")
        
        # Mock Intent Parser outcome based on rule_based
        # For simplicity in evaluation, we pass the query and let engine extract NLP signals
        input_data = {
            "query": case["query"],
            "preferences": {},
            "constraints": {},
            "user_profile": {}
        }
        
        if case.get("must_include") == "paneer":
            input_data["preferences"]["ingredients"] = ["paneer"]
            input_data["preferences"]["diet_type"] = "veg"
        elif case.get("must_include") == "chicken":
            input_data["preferences"]["ingredients"] = ["chicken"]
            
        results = engine.run(input_data, db)
        
        if not results:
            print("  ❌ FAILED: No results returned.")
            continue
            
        top_recipe = results[0]["recipe"]
        top_score = results[0]["score"]
        explanation = results[0]["explanation_text"]
        
        print(f"  Top Result: {top_recipe['name']} (Score: {top_score:.2f})")
        print(f"  Explanation: {explanation}")
        
        success = True
        
        if case.get("expected_protein_high") and (top_recipe.get("protein") or 0) < 20:
            print(f"  ❌ FAILED: Expected high protein, got {top_recipe.get('protein')}")
            success = False
            
        if case.get("expected_calorie_low") and (top_recipe.get("calories") or 999) > 500:
            print(f"  ❌ FAILED: Expected low calorie, got {top_recipe.get('calories')}")
            success = False
            
        if success:
            print("  ✅ PASSED")
            passed += 1
            
        print("-" * 40)
        
    print(f"\nEvaluation Complete: {passed}/{total} Passed.")
    print(f"Constraint Pass Rate: {(passed/total)*100:.1f}%")
    
if __name__ == "__main__":
    run_evaluation()
