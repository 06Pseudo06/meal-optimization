Here is the content converted into a clean, fully-formatted **README.md**. You can copy the block below directly into your file.

```markdown
# Meal Optimization Backend

AI-driven personalized meal recommendation engine built with **FastAPI**, **PostgreSQL**, and a deterministic optimization layer.

---

## Overview

This backend powers a personalized nutrition recommendation system that ranks recipes based on user-specific calorie and protein targets.

The system is designed with strict separation of concerns:

* **Backend Layer** → API, database, orchestration
* **AI Layer** → Pure deterministic optimization logic
* **Database Layer** → Persistent storage and logging

> **Note:** The recommendation engine is fully deterministic and does not rely on machine learning models (yet).

---

## Core Capabilities

* User authentication & profile management
* Personalized calorie & protein targets
* Recipe & ingredient management
* Constraint-based filtering
* Weighted multi-factor ranking
* Dockerized environment
* Structured recommendation logging

---

## Architecture

1.  **Client Request**
2.  **FastAPI Route**
3.  **Service Layer**
4.  **AI Engine (Pure Computation)**
5.  **Ranked Recommendations**
6.  **JSON Response**

The AI engine does not access the database and remains fully stateless.

---

## Project Structure

```text
backend/
├── app/
│   ├── api/                # FastAPI routes
│   ├── core/               # Config & database setup
│   ├── crud/               # Database operations
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Orchestration layer
│   └── ai/                 # AI decision engine
│       ├── engine.py
│       ├── feature_engine.py
│       ├── ranking_engine.py
│       ├── constraint_engine.py
│       ├── scoring_config.py
│       └── contracts/
├── alembic/                # Database migrations
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

```

---

## Personalized Recommendation Logic

Each user has a `daily_calorie_target` and a `daily_protein_target`. Recipes are ranked using normalized feature signals:

* Ingredient match ratio
* Protein alignment
* Calorie alignment
* Goal tag relevance
* Macro density efficiency

### Scoring Formula

$$score = w_1 \cdot \text{ingredient\_match} + w_2 \cdot \text{protein\_alignment} + w_3 \cdot \text{calorie\_alignment} + w_4 \cdot \text{goal\_tag\_match} + w_5 \cdot \text{macro\_density}$$

Weights are centrally defined in `app/ai/scoring_config.py`.

---

## Database Models

| Model | Description |
| --- | --- |
| **AuthUser** | Authentication identity. |
| **User** | Nutrition profile (1-to-1 relationship with AuthUser). |
| **Recipe** | Stores nutrition values and metadata. |
| **RecommendationLog** | Logs request payloads, recommended IDs, and timestamps. |

---

## Running the Backend

### 1. Build & Start

```bash
docker compose up --build

```

### 2. Stop

```bash
docker compose down

```

### 3. Reset Database (Destructive)

```bash
docker compose down -v
docker compose up --build

```

---

## API Documentation

Once running, the interactive Swagger UI is available at:
**`http://localhost:8000/docs`**

### Recommendation Endpoint

`POST /recipes/recommend`

**Query Parameter:** `user_id` (integer, required)

**Request Body:**

```json
{
  "ingredients": ["chicken", "rice"],
  "protein_min": 20,
  "calorie_max": 800,
  "goal": "muscle"
}

```

**Sample Response:**

```json
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

```

---

## Environment Variables

Configured via `.env`:
`DATABASE_URL=postgresql://user:password@db:5432/meal_optimization`

---

## Design Principles

* Deterministic optimization
* Strict separation of backend and AI logic
* Stateless AI engine
* Docker-first development
* Centralized scoring configuration
* Expandable architecture for future ML integration

---

## Future Enhancements

* Structured explainability layer
* Registration auto-profile creation
* Feedback-based adaptive scoring
* Multi-meal daily optimization
* Machine learning ranking model

**Status:** Personalized recommendation engine is functional and stable.

```

---

Since the structure is solid, would you like me to generate a **`.env.example`** file or a **`docker-compose.yml`** template to match this setup?

```
