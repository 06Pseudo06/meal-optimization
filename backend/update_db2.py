import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import engine

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE recipes ADD COLUMN updated_at INTEGER DEFAULT 0"))
        conn.commit()
        print("Added updated_at column to recipes.")
    except Exception as e:
        print("Column might already exist or error:", e)
