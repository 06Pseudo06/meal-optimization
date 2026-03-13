from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.jwt_handler import create_access_token
from app.services.token_service import rotate_refresh_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/refresh")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):

    try:
        user_id, new_refresh_token = rotate_refresh_token(db, refresh_token)

        access_token = create_access_token(user_id)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token
        }

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):

    from app.utils.token_utils import hash_token
    from app.crud.crud_refresh_token import delete_refresh_token

    token_hash = hash_token(refresh_token)

    delete_refresh_token(db, token_hash)

    return {
        "message": "Logged out successfully"
    }