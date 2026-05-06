from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app import models

from app.api.user_routes import router as user_router
from app.api.log_routes import router as log_router
from app.api.recipe_routes import router as recipe_router
from app.api.auth_routes import router as auth_router
from app.api.dashboard_routes import router as dashboard_router
from app.api import recommendation_routes
from app.api import system

app = FastAPI(title="Meal Optimization API")

from app.core.database import SessionLocal
from app.models.recipe import Recipe
import threading
import time

@app.on_event("startup")
def startup_event():
    import logging
    import sys
    import json
    from app.core.config import settings
    from sqlalchemy import text
    
    # 1. Validate Gemini
    if not settings.gemini_api_key:
        logging.error(json.dumps({"event": "startup_validation_failed", "reason": "Missing GEMINI_API_KEY"}))
        sys.exit(1)
        
    # 2. Validate DB
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        logging.error(json.dumps({"event": "startup_validation_failed", "reason": f"DB Connection Failed: {e}"}))
        sys.exit(1)
        
    logging.info(json.dumps({"event": "settings_loaded"}))
    logging.info(json.dumps({"event": "startup_validation_passed"}))

    def pre_warm_supervised():
        import logging
        for attempt in range(5):
            try:
                pre_warm_embeddings()
                break
            except Exception as e:
                logging.error(f"Pre-warm failed, retrying in {2**attempt}s: {e}")
                time.sleep(2**attempt)
                
    threading.Thread(target=pre_warm_supervised, daemon=True).start()

def pre_warm_embeddings():
    try:
        from app.ai.embedding_service import generate_offline_embeddings
        from app.core.database import SessionLocal
        
        db = SessionLocal()
        try:
            result = generate_offline_embeddings(db)
            print("Pre-warm complete:", result)
        finally:
            db.close()
    except Exception as e:
        print("Pre-warm failed:", e)

from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import ProfileNotFoundException

import uuid
import json
import logging
import traceback

RATE_LIMIT_DB = {}

@app.middleware("http")
async def metrics_and_rate_limit_middleware(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Rate Limiting
    user_id = request.headers.get("user-id") or request.headers.get("authorization")
    client_id = user_id if user_id else (request.client.host if request.client else "127.0.0.1")
    
    timestamps = [t for t in RATE_LIMIT_DB.get(client_id, []) if start_time - t < 60]
    
    if len(timestamps) >= 100:
        return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})
    
    timestamps.append(start_time)
    RATE_LIMIT_DB[client_id] = timestamps
    
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        logging.error(json.dumps({
            "event": "request_failed",
            "level": "ERROR",
            "request_id": request_id,
            "error": str(e),
            "trace": traceback.format_exc()[:500]
        }))
        status_code = 500
        response = JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
    
    # Metrics
    process_time = (time.time() - start_time) * 1000
    logging.info(json.dumps({
        "event": "request_completed",
        "level": "INFO",
        "request_id": request_id,
        "path": request.url.path,
        "method": request.method,
        "latency_ms": round(process_time, 2),
        "status_code": status_code
    }))
    
    return response

@app.exception_handler(ProfileNotFoundException)
async def profile_not_found_handler(request: Request, exc: ProfileNotFoundException):
    return JSONResponse(status_code=404, content={"detail": exc.message})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Backend running"}


# Include routers
app.include_router(user_router)
app.include_router(log_router)
app.include_router(recommendation_routes.router)
app.include_router(recipe_router)
app.include_router(dashboard_router)
app.include_router(system.router, tags=["system"])
app.include_router(auth_router)