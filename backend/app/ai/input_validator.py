def check_missing_fields(request: dict):

    required = {
        "calorie_max": "calorie limit",
        "protein_min": "protein target",
        "diet_type": "diet type"
    }

    missing = []

    for key, label in required.items():

        if request.get(key) is None:
            missing.append(label)

    return missing