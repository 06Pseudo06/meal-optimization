from sqlalchemy import Column, Integer, JSON, ForeignKey
from app.core.database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    preferred_ingredients = Column(JSON, default=dict)
