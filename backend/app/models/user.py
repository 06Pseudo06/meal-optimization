from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)


    auth_user_id = Column(
        Integer,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    daily_calorie_target = Column(Float, nullable=False)
    daily_protein_target = Column(Float, nullable=False)


    auth_user = relationship("AuthUser", back_populates="profile")

    logs = relationship("DailyLog", back_populates="user", cascade="all, delete")