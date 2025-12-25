# Backend Dockerfile Contract
# 
# Purpose: Multi-stage Dockerfile for FastAPI backend with hot-reload support
# Target: Development environment (future: production stage)
# Base Image: python:3.12-slim
# Platform: linux/amd64 (M1/M2 compatible)

# =============================================================================
# Stage 1: Base
# Purpose: System dependencies and base configuration
# =============================================================================
FROM --platform=linux/amd64 python:3.12-slim AS base

# Install system dependencies required by Python packages
# - libpq-dev: Required for psycopg3 (PostgreSQL adapter)
# - gcc: Required for compiling some Python packages
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# =============================================================================
# Stage 2: Dependencies
# Purpose: Install Python dependencies (cached layer)
# =============================================================================
FROM base AS dependencies

# Copy only dependency files first (layer caching optimization)
COPY pyproject.toml ./
COPY README.md ./

# Install Python dependencies
# --no-cache-dir: Reduce image size by not storing pip cache
# -e .: Editable install (allows source code changes without reinstall)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Install development dependencies
RUN pip install --no-cache-dir -e .[dev]

# =============================================================================
# Stage 3: Development
# Purpose: Development environment with hot-reload
# =============================================================================
FROM dependencies AS development

# Copy migration configuration (needed for entrypoint)
COPY alembic.ini ./
COPY alembic ./alembic

# Copy entrypoint script
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Source code will be mounted as volume at runtime (hot-reload)
# Volume mount: ./backend/src:/app/src

# Expose FastAPI port
EXPOSE 8000

# Health check (optional, for monitoring)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=3)"

# Entrypoint runs migrations, then starts uvicorn with hot-reload
ENTRYPOINT ["./entrypoint.sh"]

# =============================================================================
# Stage 4: Production (Future - out of scope for this feature)
# Purpose: Optimized production image without development tools
# =============================================================================
# FROM base AS production
# COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
# COPY src ./src
# COPY alembic.ini ./
# COPY alembic ./alembic
# COPY entrypoint.prod.sh ./
# RUN chmod +x entrypoint.prod.sh
# EXPOSE 8000
# ENTRYPOINT ["./entrypoint.prod.sh"]
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# =============================================================================
# Build Command (from repository root):
#   docker build -t db-query-tool-backend:dev --target development ./backend
#
# Run Command (standalone, without compose):
#   docker run -p 8000:8000 \
#     -v $(pwd)/backend/src:/app/src \
#     -v ~/.db_query:/root/.db_query \
#     -e POSTGRES_HOST=db \
#     db-query-tool-backend:dev
# =============================================================================
