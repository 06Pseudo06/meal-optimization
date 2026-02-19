from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

def create_user(db: Session, user_data: UserCreate):
    user = User(**user_data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, user_data: UserCreate):
    user = get_user(db, user_id)
    if not user:
        return None

    for key, value in user_data.model_dump().items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user
