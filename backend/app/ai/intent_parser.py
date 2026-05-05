import json
import re
from app.ai.llm_client import generate_llm_response

def validate_intent(intent):
    if not isinstance(intent, dict):
        return False
    if "ingredients" not in intent:
        return False
    return True

def normalize_intent(intent):
    if intent.get("diet_type"):
        intent["diet_type"] = intent["diet_type"].lower().strip()
        
    if not isinstance(intent.get("ingredients"), list):
        intent["ingredients"] = []
        
    intent["ingredients"] = list(set([str(i).lower().strip() for i in intent["ingredients"] if i]))
    return intent

def compute_confidence(intent):
    if not intent.get("intent_complete"):
        return 0.2
    if intent.get("_source") == "fallback":
        return 0.5
    return 0.9

def rule_based_parse(query: str) -> dict:
    print(json.dumps({"event": "fallback_trigger", "query": query, "reason": "rule_based_parse_called"}))
    current_intent = {
        "ingredients": [], "diet_type": None,
        "protein_min": None, "protein_max": None,
        "calorie_min": None, "calorie_max": None,
        "intent_complete": False,
        "_source": "fallback"
    }
    q_lower = query.lower()
    
    INGREDIENT_SYNONYMS = {
        "egg": ["egg", "omelette", "scrambled", "eggs"],
        "chicken": ["chicken", "grilled chicken"],
        "paneer": ["paneer", "cottage cheese", "panner"],
        "tofu": ["tofu", "soy"]
    }
    
    for key, synonyms in INGREDIENT_SYNONYMS.items():
        if any(syn in q_lower for syn in synonyms):
            current_intent["ingredients"] = [key]
            current_intent["intent_complete"] = True
            break
            
    if "low protein" in q_lower or "less protein" in q_lower:
        current_intent["protein_max"] = 15
        current_intent["intent_complete"] = True
    elif "high protein" in q_lower:
        current_intent["protein_min"] = 30
        current_intent["intent_complete"] = True
        
    match = re.search(r'(\d+)g protein', q_lower)
    if match:
        current_intent["protein_min"] = int(match.group(1))
        current_intent["intent_complete"] = True
        
    if "high calorie" in q_lower:
        current_intent["calorie_min"] = 600
        current_intent["intent_complete"] = True
    elif "low calorie" in q_lower or "weight loss" in q_lower:
        current_intent["calorie_max"] = 400
        current_intent["intent_complete"] = True
        
    if "non veg" in q_lower or "nonveg" in q_lower:
        current_intent["diet_type"] = "non_veg"
        current_intent["intent_complete"] = True
    elif "veg recipe" in q_lower or "veg" in q_lower:
        current_intent["diet_type"] = "veg"
        current_intent["intent_complete"] = True
        
    current_intent = normalize_intent(current_intent)
    current_intent["_confidence"] = compute_confidence(current_intent)
    print(json.dumps({"event": "intent_parsed", "source": "fallback", "confidence": current_intent["_confidence"], "query": query}))
    return current_intent

def parse_query(query: str) -> dict:
    prompt = f"""You are a strict JSON generator.

Convert user input into structured JSON.

Rules:

* Output ONLY valid JSON
* No explanation
* No markdown
* No text outside JSON
* Use null if unknown
* Output strictly matches this schema:
{{
  "ingredients": [],
  "protein_min": null,
  "protein_max": null,
  "calorie_min": null,
  "calorie_max": null,
  "diet_type": null,
  "intent_complete": boolean
}}

Examples:

Input: 'eggs'
Output:
{{ "ingredients": ["eggs"], "protein_min": null, "protein_max": null, "calorie_min": null, "calorie_max": null, "diet_type": null, "intent_complete": true }}

Input: 'high protein chicken meal'
Output:
{{ "ingredients": ["chicken"], "protein_min": 30, "protein_max": null, "calorie_min": null, "calorie_max": null, "diet_type": null, "intent_complete": true }}

Now convert:

Input: "{query}"

Output:
"""

    fallback = {
        "ingredients": [],
        "protein_min": None,
        "protein_max": None,
        "calorie_min": None,
        "calorie_max": None,
        "diet_type": None,
        "intent_complete": False
    }

    try:
        raw_response = generate_llm_response(query, prompt)
        print(json.dumps({"event": "raw_llm_output", "output": raw_response}))
        
        if not raw_response:
            return rule_based_parse(query)
        
        # JSON Cleaning: Extract substring between first { and last }
        match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                parsed = json.loads(json_str)
            except Exception:
                return rule_based_parse(query)
                
            if not isinstance(parsed, dict) or "ingredients" not in parsed:
                return rule_based_parse(query)
                
            # Ensure all keys exist
            for key in fallback.keys():
                if key not in parsed:
                    parsed[key] = fallback[key]
                    
            # Ensure ingredients is a list
            if parsed.get("ingredients") is None:
                parsed["ingredients"] = []
            elif isinstance(parsed.get("ingredients"), str):
                parsed["ingredients"] = [parsed["ingredients"]]
                
            # PART 2 - OVERRIDE intent_complete LOGIC
            if not any([
                parsed.get("ingredients"),
                parsed.get("protein_min"),
                parsed.get("calorie_min"),
                parsed.get("diet_type")
            ]):
                parsed["intent_complete"] = False
                
            parsed["_source"] = "llm"
            parsed = normalize_intent(parsed)
            parsed["_confidence"] = compute_confidence(parsed)
            
            print(json.dumps({"event": "intent_parsed", "source": "llm", "confidence": parsed["_confidence"], "query": query}))
            return parsed
        else:
            print(json.dumps({"event": "json_extraction_failed", "raw": raw_response}))
            return rule_based_parse(query)

    except Exception as e:
        print(json.dumps({"event": "intent_parsing_error", "error": str(e)}))
        return rule_based_parse(query)
