# Research: Docker Containerization & Orchestration

**Feature**: 002-docker-compose  
**Date**: December 25, 2025  
**Purpose**: Resolve technical unknowns before design phase

---

## R1: Docker Multi-Stage Build Patterns for Python/FastAPI

**Decision**: Use multi-stage Dockerfile with base, dependencies, and development stages; use pip (not Poetry) to match existing pyproject.toml setup

**Rationale**:
- Project already uses pip-based dependency management via pyproject.toml
- Multi-stage builds enable layer caching for faster rebuilds
- Separate development stage allows uvicorn hot-reload without affecting production image
- Platform-agnostic base image (`python:3.12-slim`) with explicit `--platform` flag for M1/M2 support

**Alternatives Considered**:
- **Poetry**: Would require additional tooling not currently in project; adds complexity
- **Single-stage Dockerfile**: Misses layer caching benefits; slower rebuilds
- **Separate dev/prod Dockerfiles**: Duplicates configuration; harder to maintain

**Implementation Notes**:
```dockerfile
# Stage 1: Base with system dependencies
FROM --platform=linux/amd64 python:3.12-slim as base
# Install system deps if needed (psycopg3 may need libpq)

# Stage 2: Dependencies layer (cached unless pyproject.toml changes)
FROM base as dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Stage 3: Development with source code
FROM dependencies as development
WORKDIR /app
# Source code mounted as volume for hot-reload
CMD ["uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
```

- Use `--no-cache-dir` to reduce image size
- Mount `/app/src` as volume for hot-reload in docker-compose.yml
- Uvicorn `--reload` watches for file changes automatically

---

## R2: Vite Development Server in Docker with Hot Module Replacement

**Decision**: Configure Vite with explicit host binding (`0.0.0.0`), enable WebSocket polling, and use named volume for node_modules

**Rationale**:
- Vite must bind to `0.0.0.0` (not `localhost`) to be accessible outside container
- WebSocket connections for HMR need explicit configuration in containerized environments
- Named volume for `node_modules` prevents performance issues from cross-filesystem bind mounts
- Polling mode (`{ usePolling: true }`) ensures file watching works across Docker filesystems

**Alternatives Considered**:
- **Bind mount node_modules**: Causes severe performance degradation on macOS (Docker Desktop limitation)
- **Native file watching**: Doesn't work reliably in Docker; requires polling fallback
- **Host network mode**: Not portable across OS (doesn't work on macOS Docker Desktop)

**Implementation Notes**:
```dockerfile
# Frontend Dockerfile
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
# Source mounted as volume
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

```typescript
// vite.config.ts additions
export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true, // Required for Docker
    },
    hmr: {
      clientPort: 5173, // Explicit port for HMR WebSocket
    },
  },
})
```

```yaml
# docker-compose.yml volume strategy
volumes:
  - ./frontend/src:/app/src           # Bind mount source for hot-reload
  - frontend_node_modules:/app/node_modules  # Named volume for performance
```

---

## R3: Docker Compose Service Dependencies and Health Checks

**Decision**: Use `depends_on` with `condition: service_healthy` and PostgreSQL health check; run Alembic migrations in backend entrypoint script

**Rationale**:
- `depends_on` alone doesn't wait for readiness; `service_healthy` ensures PostgreSQL is actually ready
- Health check with `pg_isready` is PostgreSQL-specific and reliable
- Alembic migrations in entrypoint script ensure schema is up-to-date before app starts
- Built-in Docker Compose functionality; no external tools needed

**Alternatives Considered**:
- **Init containers**: Not natively supported in Docker Compose; requires workarounds
- **Wait-for scripts**: External dependency (wait-for-it.sh); adds complexity
- **Retry logic in application**: Masks issues; prefer explicit orchestration

**Implementation Notes**:
```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    depends_on:
      db:
        condition: service_healthy
    entrypoint: ["/app/entrypoint.sh"]
```

```bash
# backend/entrypoint.sh
#!/bin/sh
set -e
# Run migrations
alembic upgrade head
# Start application
exec uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

- Health check runs every 5 seconds until PostgreSQL is ready
- Backend waits for healthy status before starting
- Migrations run automatically on startup

---

## R4: SQLite Persistence Strategy in Containerized Environment

**Decision**: Use bind mount for SQLite database directory (`~/.db_query` on host → `/root/.db_query` in container) with explicit UID/GID configuration

**Rationale**:
- SQLite requires file-level access; bind mount is the natural solution
- Encryption keys must persist across container restarts (same directory as DB)
- Running backend container as root (UID 0) ensures consistent permissions across host/container
- Host directory created automatically by Docker if it doesn't exist

**Alternatives Considered**:
- **Named volume**: Obscures location on host filesystem; harder to backup/inspect
- **Non-root user in container**: Requires UID/GID mapping; complex on different host OSes
- **Copy files in entrypoint**: Doesn't persist changes; defeats purpose

**Implementation Notes**:
```yaml
# docker-compose.yml
services:
  backend:
    volumes:
      - ~/.db_query:/root/.db_query  # SQLite DB and encryption key
      - ./backend/src:/app/src       # Source code for hot-reload
```

```python
# backend/src/config.py - already configured correctly
sqlite_path: Path = Path.home() / ".db_query" / "db_query.db"
encryption_key_path: Path = Path.home() / ".db_query" / "secret.key"
```

- Path.home() resolves to `/root` in container (matches volume mount)
- Both SQLite and encryption key in same directory
- Files persist on host filesystem at `~/.db_query`

---

## R5: Development vs Production Docker Configuration

**Decision**: Use single Dockerfile with multi-stage builds; `docker-compose.yml` for development, `docker-compose.override.yml` pattern for future production needs

**Rationale**:
- Multi-stage Dockerfile keeps dev and prod definitions in sync while enabling separate optimizations
- docker-compose.override.yml automatically merges with docker-compose.yml in development
- Current scope is development only; production config can be added later without changing base files
- Environment variables via .env file (already gitignored)

**Alternatives Considered**:
- **Separate Dockerfiles**: Duplicates configuration; divergence risk
- **Build args for every difference**: Makes Dockerfile complex and hard to read
- **Different compose files**: Requires explicit `-f` flags; error-prone

**Implementation Notes**:
```yaml
# docker-compose.yml - development defaults
services:
  backend:
    build:
      context: ./backend
      target: development  # Uses development stage from multi-stage Dockerfile
    environment:
      - DEBUG=true
    volumes:
      - ./backend/src:/app/src  # Hot-reload for dev only

# docker-compose.prod.yml - future production (out of scope for this feature)
services:
  backend:
    build:
      target: production  # Different stage, no source mounts
    environment:
      - DEBUG=false
```

```bash
# Development (automatic override):
docker compose up

# Production (explicit file):
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

---

## Summary

All technical unknowns have been resolved:

1. ✅ **Backend Dockerfile**: Multi-stage with pip, hot-reload via uvicorn, platform-agnostic
2. ✅ **Frontend Dockerfile**: Vite with HMR configuration, polling-based file watching, named volume for node_modules
3. ✅ **Service orchestration**: Health checks with `service_healthy` condition, Alembic in entrypoint
4. ✅ **SQLite persistence**: Bind mount to `~/.db_query`, root user for permission consistency
5. ✅ **Configuration management**: Multi-stage Dockerfiles, docker-compose.yml for development

**Ready to proceed to Phase 1: Design & Contracts**
