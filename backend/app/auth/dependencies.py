from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.auth_user import AuthUser
from app.auth.jwt_handler import verify_access_token


security = HTTPBearer()


def get_current_user(credentials = Depends(security), db: Session = Depends(get_db)):

    token = credentials.credentials

    try:
        user_id = verify_access_token(token)

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(AuthUser).filter(AuthUser.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user