from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
 
from app.schemas.user import UserResponse
from app.crud.user import get_user
 
from app.schemas.auth_user import RegisterUser, LoginUser
from app.crud.auth_user import (
    get_auth_user_by_email,
    create_auth_user,
    verify_password
)

from app.auth.dependencies import get_current_user
from app.models.auth_user import AuthUser
from app.models.user import User


router = APIRouter(prefix="/user", tags=["User"])

@router.post("/register")
def register_user(user: RegisterUser, db: Session = Depends(get_db)):

    # 1. Check if email already exists
    existing = get_auth_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Create authentication account
    new_auth_user = create_auth_user(db, user)

    # 3. Ensure nutrition profile exists
    existing_profile = db.query(User).filter(
        User.auth_user_id == new_auth_user.id
    ).first()

    if not existing_profile:
        profile = User(
            auth_user_id=new_auth_user.id,
            daily_calorie_target=2000,
            daily_protein_target=100
        )

        db.add(profile)
        db.commit()

    # 4. Return response
    return {
        "message": "User registered successfully",
        "user": {
            "id": new_auth_user.id,
            "email": new_auth_user.email,
            "first_name": new_auth_user.first_name,
            "last_name": new_auth_user.last_name
        }
    }


from app.auth.jwt_handler import create_access_token
from app.utils.token_utils import generate_refresh_token, hash_token
from app.crud.crud_refresh_token import create_refresh_token


@router.post("/login")
def login_user(user: LoginUser, db: Session = Depends(get_db)):

    db_user = get_auth_user_by_email(db, user.email)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Password incorrect")

    # create access token
    access_token = create_access_token(db_user.id)

    # create refresh token
    refresh_token = generate_refresh_token()
    token_hash = hash_token(refresh_token)

    create_refresh_token(db, db_user.id, token_hash)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name
        }
    }

@router.get("/me", response_model=UserResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):

    user = db.query(User).filter(User.auth_user_id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    return user