from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Meal Optimization API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Backend running"}


from app.core.database import Base, engine
from app import models

Base.metadata.create_all(bind=engine)


from app.api.user_routes import router as user_router

app.include_router(user_router)


from app.api.log_routes import router as log_router
app.include_router(log_router)


from app.api import recommendation_routes
app.include_router(recommendation_routes.router)


from app.api.recipe_routes import router as recipe_router
app.include_router(recipe_router)
