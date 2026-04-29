from sqlalchemy import Column, Integer, ForeignKey, Float, String
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
    daily_carbs_target = Column(Float, nullable=True)
    daily_fats_target = Column(Float, nullable=True)
    allergies = Column(String, nullable=True)
    weight_goal = Column(Float, nullable=True)
    current_weight = Column(Float, nullable=True)


    auth_user = relationship("AuthUser", back_populates="profile")

    logs = relationship("DailyLog", back_populates="user", cascade="all, delete")