#!/bin/sh
set -e

echo "========================================="
echo "Backend Container Starting"
echo "========================================="

# Wait for database to be ready
echo "Waiting for database to be ready..."
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  echo "Database is unavailable - sleeping"
  sleep 1
done
echo "Database is ready!"

# Run Alembic migrations
echo "Running database migrations..."
alembic upgrade head
echo "Migrations complete!"

# Start uvicorn with hot-reload
echo "Starting uvicorn server with hot-reload..."
echo "========================================="
exec uvicorn src.main:app \
  --reload \
  --host 0.0.0.0 \
  --port 8000 \
  --log-level info
