#!/bin/sh

echo "Starting backend container..."

echo "Waiting for database..."

while ! pg_isready -h db -p 5432 -U postgres
do
  echo "Database not ready yet..."
  sleep 2
done

echo "Database is ready."

echo "Running migrations..."
alembic upgrade head

echo "Running seeders..."
python -m app.seed.run_seeds

echo "Starting FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload