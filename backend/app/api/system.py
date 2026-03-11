from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.core.version import APP_NAME, VERSION, ENVIRONMENT

router = APIRouter(prefix="/system", tags=["System"])

 
@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception:
        return {
            "status": "error",
            "database": "disconnected"
        }


@router.get("/version")
def version_info():
    return {
        "Application": APP_NAME,
        "Version": VERSION,
        "Environment": ENVIRONMENT
    } 