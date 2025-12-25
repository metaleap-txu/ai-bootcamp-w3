#!/bin/bash
# Backend Entrypoint Script Contract
#
# Purpose: Run database migrations before starting FastAPI application
# Usage: Called automatically by Docker container CMD
# Prerequisites: Database must be healthy (depends_on: service_healthy)

set -e  # Exit on any error

echo "========================================="
echo "Backend Container Starting"
echo "========================================="

# Wait for database to be ready (redundant with health check, but defensive)
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

# =============================================================================
# Notes:
# - This script MUST be executable (chmod +x entrypoint.sh)
# - Database connection parameters from environment variables:
#   - POSTGRES_HOST (service name 'db')
#   - POSTGRES_PORT (default 5432)
#   - POSTGRES_USER (default postgres)
# - uvicorn --reload watches /app/src for changes (bind mounted volume)
# - exec ensures uvicorn receives signals properly (e.g., SIGTERM for shutdown)
# =============================================================================
