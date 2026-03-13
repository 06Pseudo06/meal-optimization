---

# 🍽️ Meal Optimization Backend

An AI-driven personalized meal recommendation engine built with **FastAPI**, **PostgreSQL**, and a deterministic optimization core.

---

## 📌 Overview

This backend powers a **personalized nutrition recommendation system** that ranks recipes based on user-specific caloric and macronutrient targets.

### Architectural Layers

| Layer | Responsibility |
| --- | --- |
| **API Backend** | Route handling, orchestration, and DB persistence |
| **AI Engine** | Stateless, deterministic ranking and constraint logic |
| **Database** | Relational storage for profiles, recipes, and logs |

> [!IMPORTANT]
> **Design Principle:** The AI engine is strictly **stateless**. It never accesses the database directly; it receives structured features and returns ranked outputs to the service layer.

---

## 🧠 System Architecture

### Logic Flow

1. **Client Request**: User submits preferences or a recommendation trigger.
2. **Service Layer**: Fetches relevant candidate recipes and user profile data from PostgreSQL.
3. **AI Engine**: Processes features (Protein, Calories, Ingredients) using weighted logic.
4. **Ranking**: Returns a sorted list of recipes with scoring explanations.
5. **Response**: FastAPI delivers a structured JSON payload to the client.

---

---

## 🔐 Authentication System

The backend implements a **JWT-based authentication system** with secure refresh token rotation.

### Components

| Component | Purpose |
|---|---|
| **Access Token (JWT)** | Short-lived token used to authorize API requests |
| **Refresh Token** | Long-lived token used to generate new access tokens |
| **Refresh Token Rotation** | Old refresh tokens are invalidated when new ones are issued |

### Flow

1. User registers or logs in.
2. Server issues:
   - **Access Token**
   - **Refresh Token**
3. Access token is sent with protected API requests.
4. When expired, client calls `/auth/refresh` using the refresh token.
5. A new access token is issued and the old refresh token is invalidated.

Protected endpoints include:

- `/recipes/recommend`
- `/logs/*`
- `/user/me`

## 📁 Project Structure

```text
backend/
├── app/
│   ├── api/                 # FastAPI route definitions
│   ├── core/                # Config, security, DB session
│   ├── crud/                # Database operations
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic & orchestration
│   ├── ai/                  # Recommendation engine
│   │   ├── engine.py
│   │   ├── constraint_engine.py
│   │   ├── feature_engine.py
│   │   ├── ranking_engine.py
│   │   └── scoring_config.py
│   ├── utils/               # Token hashing & helpers
│   └── seed/                # Database seeding scripts
│
├── alembic/                 # Migration history
├── data/                    # CSV datasets
├── Dockerfile
├── docker-compose.yml
└── start.sh

```

---

## 🍗 Recommendation Logic

The engine calculates a multi-factor score for each recipe based on the following signals:

| Feature | Scoring Logic |
| --- | --- |
| **Ingredient Match** | Jaccard similarity between user pantry and recipe requirements |
| **Protein Alignment** | L1 distance from `daily_protein_target` |
| **Calorie Alignment** | Proximity to `daily_calorie_target` |
| **Goal Tag Match** | Binary check against user goals (e.g., "Muscle Gain", "Keto") |
| **Macro Density** | Nutritional efficiency (Protein-to-Calorie ratio) |

Weights are centrally managed in `app/ai/scoring_config.py` for easy tuning without code changes.   

Each recommendation request is stored for analysis and debugging.

Logged information includes:

- User ID
- Requested ingredients
- Returned recipe IDs
- Timestamp

This allows future features such as:

- User recommendation history
- Feedback-based learning
- AI explainability

---

## 🚀 Getting Started

### 1️⃣ Start the System

```bash
docker compose up --build

```

**Startup Pipeline:**

1. **PostgreSQL**: Container initializes and runs health checks.
2. **Migrations**: `Alembic` applies latest schema changes.
3. **Seeding**: `run_seeds.py` populates recipes and ingredients from CSVs.
4. **Server**: Uvicorn starts the FastAPI application.

### 2️⃣ API Exploration

Once running, access the interactive documentation at:

* **Swagger UI**: [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)
* **ReDoc**: [http://localhost:8000/redoc](https://www.google.com/search?q=http://localhost:8000/redoc)

---

## 📥 Example Request

**Endpoint:** `POST /recipes/recommend 
               Authorization: Bearer <access_token>`

**Request Body:**

```json
{
  "ingredients": ["chicken", "rice"],
  "protein_min": 20,
  "calorie_max": 800,
  "goal": "muscle"
}

```

**Example Response:**

```json
[
  {
    "id": 18,
    "name": "Chicken Biryani",
    "score": 0.895,
    "explanation": {
      "protein_alignment": 0.93,
      "calorie_alignment": 0.85,
      "ingredient_match": 0.90
    }
  }
]

```

---

## 🔮 Future Roadmap

- Feedback-based adaptive scoring
- Multi-meal daily optimization
- Ingredient substitution engine
- Recommendation history API
- User nutrition analytics dashboard
- Machine learning ranking model
---
