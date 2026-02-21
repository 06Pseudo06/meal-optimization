from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from pydantic import BaseModel

# Nutrition user (targets/logs)
from app.schemas.user import UserCreate, UserResponse
from app.crud.user import create_user, get_user, update_user

# Auth user
from app.schemas.auth_user import RegisterUser, LoginUser
from app.crud.auth_user import get_auth_user_by_email, create_auth_user, authenticate_auth_user, verify_password


class UserLogin(BaseModel):
    email: str
    password: str

router = APIRouter(prefix="/user", tags=["User"])

@router.post("/", response_model=UserResponse)
def create_user_route(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.get("/{user_id}", response_model=UserResponse)
def get_user_route(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/login")
def login_user(user: LoginUser, db: Session = Depends(get_db)):
    db_user = get_auth_user_by_email(db, user.email)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Password incorrect")

    return {
        "message": "Login successful",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
        },
    }

@router.post("/register")
def register_user(user: RegisterUser, db: Session = Depends(get_db)):
    existing = get_auth_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = create_auth_user(db, user)

    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
        }
    }