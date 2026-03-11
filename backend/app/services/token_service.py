from sqlalchemy.orm import Session
from datetime import datetime

from app.utils.token_utils import hash_token, generate_refresh_token
from app.crud.crud_refresh_token import (
    get_refresh_token,
    delete_refresh_token,
    create_refresh_token
)


def rotate_refresh_token(db: Session, refresh_token: str):

    token_hash = hash_token(refresh_token)

    db_token = get_refresh_token(db, token_hash)

    if not db_token:
        raise Exception("Invalid refresh token")

    if db_token.expires_at < datetime.utcnow():
        delete_refresh_token(db, token_hash)
        raise Exception("Refresh token expired")

    user_id = db_token.user_id

    # delete old token
    delete_refresh_token(db, token_hash)

    # create new token
    new_token = generate_refresh_token()

    new_hash = hash_token(new_token)

    create_refresh_token(db, user_id, new_hash)

    return user_id, new_token

