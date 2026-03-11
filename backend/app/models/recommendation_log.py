from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from datetime import datetime
from app.core.database import Base


class RecommendationLog(Base):

    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("auth_users.id"))

    ingredients = Column(Text)

    recommended_recipe_ids = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow) 