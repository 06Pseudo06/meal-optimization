import re

def parse_user_input(text):

    text = text.lower()

    result = {
        "calorie_max": None,
        "protein_min": None,
        "diet_type": None,
        "goal": None,
        "time_of_day": None,
        "exclude_ingredients": []
    }

    # ----------------
    # Typo fixes
    # ----------------
    text = text.replace("brekfast", "breakfast")
    text = text.replace("protien", "protein")
    text = text.replace("calries", "calories")

    # ----------------
    # Calories
    # ----------------
    num = re.search(r'(\d+)', text)

    if num and any(x in text for x in ["under", "below", "less than", "max"]):
        result["calorie_max"] = int(num.group(1))

    # ----------------
    # Protein
    # ----------------
    if any(x in text for x in [
        "high protein",
        "protein rich",
        "gym ke liye",
        "gym meal"
    ]):
        result["protein_min"] = 30

    # ----------------
    # Time
    # ----------------
    if any(x in text for x in ["breakfast", "nashta"]):
        result["time_of_day"] = "breakfast"

    elif "lunch" in text:
        result["time_of_day"] = "lunch"

    elif any(x in text for x in ["dinner", "raat"]):
        result["time_of_day"] = "dinner"

    # ----------------
    # Goal
    # ----------------
    if any(x in text for x in [
        "weight loss",
        "fat loss",
        "lose weight"
    ]):
        result["goal"] = "fat_loss"

    if any(x in text for x in [
        "muscle gain",
        "bulk"
    ]):
        result["goal"] = "muscle_gain"

    # ----------------
    # Diet
    # ----------------
    if "veg" in text:
        result["diet_type"] = "veg"

    # ----------------
    # Exclusions
    # ----------------
    foods = ["egg", "onion", "garlic", "milk"]

    for food in foods:
        if f"no {food}" in text or f"{food} nahi" in text:
            result["exclude_ingredients"].append(food)

    return result