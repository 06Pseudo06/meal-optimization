from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.auth_user import AuthUser
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_auth_user_by_email(db: Session, email: str):
    return db.query(AuthUser).filter(AuthUser.email == email).first()


def create_auth_user(db: Session, user):
    hashed_password = get_password_hash(user.password)

    db_user = AuthUser(
        first_name=user.first_name,
        last_name=user.last_name,
        age=user.age,
        gender=user.gender,
        phone=user.phone,
        email=user.email,
        password_hash=hashed_password,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # CREATE NUTRITION PROFILE
    profile = User(
        auth_user_id=db_user.id,
        daily_calorie_target=0,
        daily_protein_target=0,
    )

    db.add(profile)
    db.commit()

    return db_user


def authenticate_auth_user(db: Session, email: str, password: str):
    user = get_auth_user_by_email(db, email)
    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user