from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app import models

from app.api.user_routes import router as user_router
from app.api.log_routes import router as log_router
from app.api.recipe_routes import router as recipe_router
from app.api.auth_routes import router as auth_router
from app.api import recommendation_routes
from app.api import system

app = FastAPI(title="Meal Optimization API")

from app.core.database import SessionLocal
from app.models.recipe import Recipe
import threading
import time

@app.on_event("startup")
def startup_event():
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
        from app.ai.engine import embedder, RECIPE_EMBEDDING_CACHE
        if not embedder:
            return
            
        db = SessionLocal()
        try:
            recipes = db.query(Recipe).all()
            pending = []
            for r in recipes:
                if not r.embedding:
                    desc = getattr(r, "description", "") or ""
                    text = f"{r.name} {desc}".strip()
                    emb = embedder.encode(text).tolist()
                    r.embedding = emb
                    pending.append(r)
                
                RECIPE_EMBEDDING_CACHE[r.id] = {
                    "emb": r.embedding,
                    "updated_at": getattr(r, "updated_at", 0)
                }
            
            if pending:
                db.commit()
                print(f"Pre-warmed and stored embeddings for {len(pending)} recipes.")
        finally:
            db.close()
    except Exception as e:
        print("Pre-warm failed:", e)

from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import ProfileNotFoundException

RATE_LIMIT_DB = {}

@app.middleware("http")
async def metrics_and_rate_limit_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Rate Limiting
    user_id = request.headers.get("user-id") or request.headers.get("authorization")
    client_id = user_id if user_id else (request.client.host if request.client else "127.0.0.1")
    
    timestamps = [t for t in RATE_LIMIT_DB.get(client_id, []) if start_time - t < 60]
    
    if len(timestamps) >= 100:
        return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})
    
    timestamps.append(start_time)
    RATE_LIMIT_DB[client_id] = timestamps
    
    response = await call_next(request)
    
    # Metrics
    process_time = (time.time() - start_time) * 1000
    import logging
    import json
    logging.info(json.dumps({
        "event": "request_completed",
        "path": request.url.path,
        "method": request.method,
        "latency_ms": round(process_time, 2),
        "status_code": response.status_code
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
app.include_router(system.router, tags=["system"])
app.include_router(auth_router)