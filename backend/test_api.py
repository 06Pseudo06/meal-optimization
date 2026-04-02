import requests
import json

BASE_URL = "http://localhost:8000"

print("--- Testing Phase 2 ---")

# Login 
login_payload = {
    "email": "test2@test.com",
    "password": "Password123!"
}

res = requests.post(f"{BASE_URL}/user/login", json=login_payload)
token = res.json().get("access_token")

headers = {
    "Authorization": f"Bearer {token}"
}

# 1. Update Preferences
prefs_payload = {
    "allergies": "peanuts, shell-fish"
}
res = requests.patch(f"{BASE_URL}/user/me/preferences", json=prefs_payload, headers=headers)
print("PATCH Preferences:", res.status_code, res.text)

# 2. History
res = requests.get(f"{BASE_URL}/recipes/history", headers=headers)
print("GET History:", res.status_code, res.text)
