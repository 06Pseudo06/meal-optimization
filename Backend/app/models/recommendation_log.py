from sqlalchemy import Column, Integer, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Store request payload
    request_payload = Column(JSON, nullable=False)

    # Store recommended recipe IDs
    recommended_recipe_ids = Column(JSON, nullable=False)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
