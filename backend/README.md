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

## 📁 Project Structure

```text
backend/
├── app/
│   ├── api/             # FastAPI route definitions
│   ├── core/            # Global config & DB session management
│   ├── crud/            # SQL Alchemy CRUD operations
│   ├── models/          # Database schemas (SQLAlchemy)
│   ├── schemas/         # Data validation (Pydantic)
│   ├── services/        # Business logic & AI orchestration
│   ├── ai/              # The "Brain": Ranking & Scoring logic
│   │   ├── engine.py
│   │   ├── ranking_engine.py
│   │   └── scoring_config.py
│   └── seed/            # Data initialization scripts
├── alembic/             # Database migration history
├── data/                # Source CSV datasets
└── docker-compose.yml   # Multi-container orchestration

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

**Endpoint:** `POST /recipes/recommend?user_id=1`

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

* **Feedback Loop**: Implement an adaptive scoring layer based on user "dislike/like" history.
* **Explainability**: Enhanced natural language explanations for *why* a meal was recommended.
* **Multi-Meal Optimization**: Generating full-day meal plans that hit exact daily totals.
* **ML Integration**: Transition from deterministic weights to a Learning-to-Rank (LTR) model.

---
