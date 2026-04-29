import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import engine, Base
import app.models

print("Attempting database reset...")
try:
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS user_history CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS user_profiles CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS recipes CASCADE;"))
        print("Dropped corrupted tables cleanly.")
except Exception as e:
    print("Drop error:", e)

try:
    Base.metadata.create_all(bind=engine)
    print("Recreated schema from SQLAlchemy models safely.")
except Exception as e:
    print("Create error:", e)
