# 🍽️ Meal Optimization Backend

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![Status](https://img.shields.io/badge/Status-Stable-success)

AI-driven personalized meal recommendation backend built with **FastAPI**, **PostgreSQL**, and a deterministic optimization engine.

---

# 📌 Overview

This backend powers a **personalized nutrition recommendation system** that ranks recipes based on user-specific calorie and protein targets.

The system is designed with strict separation of responsibilities:

| Layer | Responsibility |
|------|------|
| Backend | API routes, orchestration, database access |
| AI Engine | Deterministic ranking logic |
| Database | Persistent storage and logging |

The recommendation engine is currently **fully deterministic** and does **not rely on machine learning models**.

---

# ⚙️ Core Capabilities

- User authentication & profile management
- Personalized calorie & protein targets
- Recipe & ingredient management
- Constraint-based filtering
- Weighted multi-factor ranking
- Automatic database migrations
- Automated seed dataset loading
- Dockerized development environment
- Structured recommendation logging

---

# 🧠 System Architecture


Client Request
↓
FastAPI Route
↓
Service Layer
↓
AI Engine (Stateless)
↓
Ranked Recommendations
↓
JSON Response


Important design principle:

> The **AI engine never accesses the database directly**.  
> It only receives structured features and returns ranked outputs.

---

# 📁 Project Structure


backend/
│
├── app/
│ ├── api/ # FastAPI routes
│ ├── core/ # Config & database setup
│ ├── crud/ # Database operations
│ ├── models/ # SQLAlchemy models
│ ├── schemas/ # Pydantic schemas
│ ├── services/ # Business logic layer
│ │
│ ├── ai/ # Recommendation engine
│ │ ├── engine.py
│ │ ├── feature_engine.py
│ │ ├── ranking_engine.py
│ │ ├── constraint_engine.py
│ │ └── scoring_config.py
│ │
│ └── seed/ # Dataset initialization
│ ├── seed_recipes.py
│ ├── seed_ingredients.py
│ ├── seed_mappings.py
│ └── run_seeds.py
│
├── alembic/ # Database migrations
├── data/ # CSV datasets
├── start.sh # Container startup pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md


---

# 🍗 Recommendation Logic

Each user profile defines:


daily_calorie_target
daily_protein_target


Recipes are ranked using normalized feature signals.

| Feature | Description |
|------|------|
| Ingredient Match | Overlap between user ingredients and recipe ingredients |
| Protein Alignment | Distance from protein target |
| Calorie Alignment | Distance from calorie target |
| Goal Tag Match | Goal-based tag relevance |
| Macro Density | Nutritional efficiency score |

Weights are centrally defined in:


app/ai/scoring_config.py


---

# 🗄️ Database Models

| Model | Description |
|------|------|
| **AuthUser** | Authentication identity |
| **User** | Nutrition profile |
| **Recipe** | Nutrition values & metadata |
| **Ingredient** | Ingredient catalog |
| **RecipeIngredient** | Recipe ↔ Ingredient mapping |
| **RecommendationLog** | Logs recommendation events |
| **DailyLog** | Tracks daily activity |

---

# 🚀 Running the Backend

## 1️⃣ Start the System

```bash
docker compose up --build

Startup pipeline:

PostgreSQL container starts
        ↓
Healthcheck confirms DB ready
        ↓
Backend container starts
        ↓
Alembic migrations run
        ↓
Seed dataset loads
        ↓
FastAPI server starts
2️⃣ Stop Containers
docker compose down
3️⃣ Reset Database (Destructive)
docker compose down -v
docker compose up --build

This removes the database volume and rebuilds everything.

📚 API Documentation

Swagger UI:

http://localhost:8000/docs
📥 Example Recommendation Request

Endpoint:

POST /recipes/recommend

Query Parameter:

user_id: integer
Request Body
{
  "ingredients": ["chicken", "rice"],
  "protein_min": 20,
  "calorie_max": 800,
  "goal": "muscle"
}
Example Response
[
  {
    "id": 18,
    "name": "Chicken Biryani",
    "calories": 750,
    "protein": 38,
    "score": 0.496583,
    "explanation": {
      "ingredient_match": 0,
      "protein_alignment": 0.6333,
      "calorie_alignment": 0.9375,
      "goal_tag_match": 0,
      "macro_density": 0.1688
    }
  }
]
🖥 Database GUI

pgAdmin is included for database inspection.

Open:

http://localhost:5050

Login:

Email: admin@meal.com
Password: admin

Database host inside Docker network:

db
🌱 Environment Variables

Example .env

DATABASE_URL=postgresql://postgres:postgres@db:5432/meal_optimization
🧩 Design Principles

Deterministic optimization

Strict separation of backend and AI logic

Stateless AI engine

Docker-first development

Centralized scoring configuration

Expandable architecture for ML integration

🔮 Future Enhancements

Planned improvements:

Structured explainability layer

Automatic profile creation during registration

Feedback-based adaptive scoring

Multi-meal daily optimization

ML-based ranking models

📊 Status

✅ Backend infrastructure stable
✅ Recommendation engine functional
✅ Dockerized development environment

```
