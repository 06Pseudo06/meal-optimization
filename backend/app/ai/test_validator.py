from app.ai.nlp_parser import parse_user_input
from app.ai.input_validator import check_missing_fields

query = "I need breakfast under 400 calories"

request = parse_user_input(query)

missing = check_missing_fields(request)

if missing:
    print("Please provide:", ", ".join(missing))
else:
    print("All important inputs received.")
    print(request)
    