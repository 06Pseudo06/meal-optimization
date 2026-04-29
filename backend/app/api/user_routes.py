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

from app.core.security import create_access_token

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

    from app.core.exceptions import ProfileNotFoundException
    if not user:
        raise ProfileNotFoundException()

    return user

from app.schemas.user import UserPreferencesUpdate

@router.patch("/me/preferences", response_model=UserResponse)
def update_my_preferences(
    prefs: UserPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    user = db.query(User).filter(User.auth_user_id == current_user.id).first()
    
    from app.core.exceptions import ProfileNotFoundException
    if not user:
        raise ProfileNotFoundException()
    
    if prefs.allergies is not None:
        user.allergies = prefs.allergies
    if prefs.daily_calorie_target is not None:
        user.daily_calorie_target = prefs.daily_calorie_target
    if prefs.daily_protein_target is not None:
        user.daily_protein_target = prefs.daily_protein_target
    if prefs.daily_carbs_target is not None:
        user.daily_carbs_target = prefs.daily_carbs_target
    if prefs.daily_fats_target is not None:
        user.daily_fats_target = prefs.daily_fats_target
    if prefs.weight_goal is not None:
        user.weight_goal = prefs.weight_goal
    if prefs.current_weight is not None:
        user.current_weight = prefs.current_weight
        
    db.commit()
    db.refresh(user)

    return user

from app.models.daily_log import DailyLog
from app.models.recommendation_log import RecommendationLog
from app.crud.auth_user import verify_password
from pydantic import BaseModel

class DeleteAccountRequest(BaseModel):
    password: str

@router.post("/me/clear-data")
def clear_user_data(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    user = db.query(User).filter(User.auth_user_id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Delete Daily Logs
    db.query(DailyLog).filter(DailyLog.user_id == user.id).delete()
    
    # Delete Recommendation Logs
    db.query(RecommendationLog).filter(RecommendationLog.user_id == current_user.id).delete()

    # Reset Preferences
    user.daily_calorie_target = 2000
    user.daily_protein_target = 100
    user.daily_carbs_target = None
    user.daily_fats_target = None
    user.weight_goal = None
    user.current_weight = None
    user.allergies = None

    db.commit()
    return {"message": "Data cleared successfully"}

@router.post("/me/delete-account")
def delete_account(
    request: DeleteAccountRequest,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    if not verify_password(request.password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="password does not match")

    user = db.query(User).filter(User.auth_user_id == current_user.id).first()
    
    if user:
        db.query(DailyLog).filter(DailyLog.user_id == user.id).delete()
        db.delete(user)

    db.query(RecommendationLog).filter(RecommendationLog.user_id == current_user.id).delete()
    
    # Delete refresh tokens
    from app.models.refresh_token import RefreshToken
    db.query(RefreshToken).filter(RefreshToken.user_id == current_user.id).delete()

    db.delete(current_user)
    db.commit()
    
    return {"message": "Account deleted successfully"}