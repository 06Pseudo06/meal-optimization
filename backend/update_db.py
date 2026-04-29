import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import engine, Base
import app.models

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE recipes ADD COLUMN embedding JSON"))
        conn.commit()
        print("Added embedding column to recipes.")
    except Exception as e:
        print("Column might already exist or error:", e)

Base.metadata.create_all(bind=engine)
print("Created tables.")
