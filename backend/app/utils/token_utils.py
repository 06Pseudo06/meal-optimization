import hashlib

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


import secrets

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)