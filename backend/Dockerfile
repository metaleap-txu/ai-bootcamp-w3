# Backend Dockerfile for Database Query Tool
# Multi-stage build for development environment

# =============================================================================
# Stage 1: Base
# =============================================================================
FROM --platform=linux/amd64 python:3.12-slim AS base

# Install system dependencies required by Python packages
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# =============================================================================
# Stage 2: Dependencies
# =============================================================================
FROM base AS dependencies

# Copy dependency files
COPY pyproject.toml ./
RUN echo "README.md placeholder for editable install" > README.md

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir -e .[dev]

# =============================================================================
# Stage 3: Development
# =============================================================================
FROM dependencies AS development

# Copy migration configuration
COPY alembic.ini ./
COPY alembic ./alembic

# Copy entrypoint script
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Source code will be mounted as volume at runtime (hot-reload)
# Volume mount: ./backend/src:/app/src

# Expose FastAPI port
EXPOSE 8000

# Entrypoint runs migrations, then starts uvicorn with hot-reload
ENTRYPOINT ["./entrypoint.sh"]
