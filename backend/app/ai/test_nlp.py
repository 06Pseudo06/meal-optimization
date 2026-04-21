from app.ai.nlp_parser import parse_user_input
from pprint import pprint

query = "Mujhe gym ke liye brekfast chahiye under 400 cal no egg"

result = parse_user_input(query)

pprint(result, sort_dicts=False, width=100)