from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    daily_calorie_target = Column(Float, nullable=False)
    daily_protein_target = Column(Float, nullable=False)

    logs = relationship("DailyLog", back_populates="user", cascade="all, delete")
