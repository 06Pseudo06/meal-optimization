from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.refresh_token import RefreshToken


def create_refresh_token(db: Session, user_id: int, token_hash: str):

    expires = datetime.utcnow() + timedelta(days=7)

    token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires
    )

    db.add(token)
    db.commit()
    db.refresh(token)

    return token


def get_refresh_token(db: Session, token_hash: str):

    return db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()


def delete_refresh_token(db: Session, token_hash: str):

    token = get_refresh_token(db, token_hash)

    if token:
        db.delete(token)
        db.commit()