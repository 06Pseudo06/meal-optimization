from sqlalchemy import Column, Integer, Boolean, ForeignKey
from app.core.database import Base

class UserHistory(Base):
    __tablename__ = "user_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"))
    timestamp = Column(Integer)
    liked = Column(Boolean, default=True)
