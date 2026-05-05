import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.ai.intent_parser import parse_query
from app.services.recommendation_service import merge_intent

queries = [
    "hi",
    "eggs",
    "veg low calorie",
    "high protein chicken meal",
    "something healthy",
    "reset",
    "asdfasdfasdf"
]

print("--- TESTING INTENT PARSER ---")
for q in queries:
    print(f"\nQuery: '{q}'")
    try:
        res = parse_query(q)
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error: {e}")

print("\n--- TESTING SAFE MEMORY MERGE ---")
memory = {
    "ingredients": ["chicken"],
    "diet_type": None,
    "protein_min": 30,
    "protein_max": None,
    "calorie_min": None,
    "calorie_max": 800
}

new_intent = {
    "ingredients": ["tofu"],
    "diet_type": "veg",
    "protein_min": None,
    "protein_max": 40,
    "calorie_min": 500,
    "calorie_max": None
}

print(f"Memory: {memory}")
print(f"New Intent: {new_intent}")
merged = merge_intent(memory, new_intent)
print(f"Merged Intent: {merged}")
