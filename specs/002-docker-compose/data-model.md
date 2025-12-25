# Data Model: Docker Containerization

**Feature**: 002-docker-compose  
**Date**: December 25, 2025  
**Purpose**: Define Docker-specific entities and their relationships

---

## Container Images

### Backend Image
- **Name**: `db-query-tool-backend`
- **Tag**: `dev` (development), `latest` (future production)
- **Base Image**: `python:3.12-slim`
- **Platform**: `linux/amd64` (explicit for M1/M2 compatibility)
- **Stages**:
  - `base`: System dependencies
  - `dependencies`: Python packages from pyproject.toml
  - `development`: Source code with hot-reload

### Frontend Image
- **Name**: `db-query-tool-frontend`
- **Tag**: `dev` (development), `latest` (future production)
- **Base Image**: `node:20-slim`
- **Platform**: `linux/amd64`
- **Stages**: Single-stage for development (multi-stage for future production)

### Database Image
- **Name**: `postgres` (official image)
- **Tag**: `15-alpine`
- **Platform**: Multi-arch (Docker official)

---

## Services

### Service: backend
- **Container Name**: `db-query-tool-backend`
- **Image**: Built from `./backend/Dockerfile`
- **Ports**: 
  - Host: `8000` → Container: `8000` (FastAPI)
- **Dependencies**: 
  - `db` (with `condition: service_healthy`)
- **Health Check**: None (relies on uvicorn startup)
- **Restart Policy**: `unless-stopped`
- **Networks**: `app-network`

### Service: frontend
- **Container Name**: `db-query-tool-frontend`
- **Image**: Built from `./frontend/Dockerfile`
- **Ports**: 
  - Host: `5173` → Container: `5173` (Vite dev server)
- **Dependencies**: None (can start independently)
- **Health Check**: None (Vite dev server)
- **Restart Policy**: `unless-stopped`
- **Networks**: `app-network`

### Service: db
- **Container Name**: `db-query-tool-db`
- **Image**: `postgres:15-alpine`
- **Ports**: 
  - Host: `5432` → Container: `5432` (PostgreSQL)
- **Dependencies**: None (foundational service)
- **Health Check**: 
  - Test: `pg_isready -U postgres`
  - Interval: 5s
  - Timeout: 5s
  - Retries: 5
- **Restart Policy**: `unless-stopped`
- **Networks**: `app-network`

---

## Volumes

### Named Volumes

#### frontend_node_modules
- **Type**: Named volume
- **Purpose**: Store npm dependencies for performance
- **Mount Point**: Container `/app/node_modules`
- **Lifecycle**: Persist across container restarts; recreated on image rebuild
- **Rationale**: Avoid slow cross-filesystem bind mounts on macOS

#### postgres_data
- **Type**: Named volume
- **Purpose**: Persist PostgreSQL database data
- **Mount Point**: Container `/var/lib/postgresql/data`
- **Lifecycle**: Persist until explicit removal (`docker compose down -v`)
- **Rationale**: Database durability across container restarts

### Bind Mounts

#### Backend Source Code
- **Type**: Bind mount
- **Source**: `./backend/src` (host)
- **Target**: `/app/src` (container)
- **Purpose**: Enable hot-reload for development
- **Read-Only**: No (source code changes)

#### Frontend Source Code
- **Type**: Bind mount
- **Source**: `./frontend/src` (host)
- **Target**: `/app/src` (container)
- **Purpose**: Enable HMR (Hot Module Replacement) for development
- **Read-Only**: No (source code changes)

#### SQLite Database Directory
- **Type**: Bind mount
- **Source**: `~/.db_query` (host user home)
- **Target**: `/root/.db_query` (container root home)
- **Purpose**: Persist SQLite database and encryption key across container restarts
- **Read-Only**: No (database writes, key generation)
- **Contains**:
  - `db_query.db` (SQLite database file)
  - `secret.key` (Encryption key for credentials)

#### Alembic Migrations
- **Type**: Bind mount
- **Source**: `./backend/alembic` (host)
- **Target**: `/app/alembic` (container)
- **Purpose**: Access migration files for `alembic upgrade head` in entrypoint
- **Read-Only**: Yes (migrations are read-only at runtime)

#### Alembic Configuration
- **Type**: Bind mount
- **Source**: `./backend/alembic.ini` (host)
- **Target**: `/app/alembic.ini` (container)
- **Purpose**: Alembic configuration for database connection string
- **Read-Only**: Yes

---

## Networks

### app-network
- **Driver**: bridge (default)
- **Purpose**: Isolate application services from other containers
- **Services**: backend, frontend, db
- **DNS**: Automatic service discovery by service name
  - Backend can reach database via `db:5432`
  - Frontend can reach backend via `backend:8000` (but uses host port in browser)

---

## Environment Variables

### Service: backend
| Variable | Value | Source | Purpose |
|----------|-------|--------|---------|
| `DEBUG` | `true` | docker-compose.yml | Enable FastAPI debug mode |
| `POSTGRES_HOST` | `db` | docker-compose.yml | PostgreSQL host (service name) |
| `POSTGRES_PORT` | `5432` | docker-compose.yml | PostgreSQL port |
| `POSTGRES_USER` | `postgres` | docker-compose.yml | PostgreSQL username |
| `POSTGRES_PASSWORD` | `postgres` | docker-compose.yml | PostgreSQL password (dev only) |
| `POSTGRES_DB` | `dbquery` | docker-compose.yml | PostgreSQL database name |
| `OPENAI_API_KEY` | `${OPENAI_API_KEY}` | .env file | OpenAI API for NL2SQL |

### Service: frontend
| Variable | Value | Source | Purpose |
|----------|-------|--------|---------|
| `VITE_API_URL` | `http://localhost:8000` | docker-compose.yml | Backend API URL (browser context) |

### Service: db
| Variable | Value | Source | Purpose |
|----------|-------|--------|---------|
| `POSTGRES_USER` | `postgres` | docker-compose.yml | Database superuser |
| `POSTGRES_PASSWORD` | `postgres` | docker-compose.yml | Superuser password |
| `POSTGRES_DB` | `dbquery` | docker-compose.yml | Initial database name |

---

## File System Layout

### Backend Container (`/app`)
```
/app/
├── src/                    # Source code (bind mounted, hot-reload)
│   ├── main.py
│   ├── config.py
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── utils/
├── alembic/               # Migrations (bind mounted, read-only)
├── alembic.ini           # Alembic config (bind mounted, read-only)
├── pyproject.toml        # Copied during build
├── entrypoint.sh         # Runs migrations + starts uvicorn
└── /root/.db_query/      # SQLite data (bind mounted)
    ├── db_query.db
    └── secret.key
```

### Frontend Container (`/app`)
```
/app/
├── src/                  # Source code (bind mounted, HMR)
│   ├── App.tsx
│   ├── main.tsx
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── types/
├── node_modules/         # Named volume (performance)
├── package.json          # Copied during build
├── vite.config.ts       # Copied during build (with Docker-specific config)
└── tsconfig.json        # Copied during build
```

### Database Container (`/var/lib/postgresql/data`)
```
/var/lib/postgresql/data/  # Named volume (postgres_data)
└── [PostgreSQL data files]
```

---

## Data Flow

### Service Communication
```
Browser (localhost:5173)
    ↓ HTTP
Frontend Container :5173
    ↓ HTTP/WebSocket (HMR)
    ↓
Host Network (Docker bridge)
    ↓
Backend Container :8000
    ↓ PostgreSQL protocol
Database Container :5432
```

### Development Hot-Reload Flow
```
Developer edits ./backend/src/main.py (host)
    ↓ Bind mount sync
Container /app/src/main.py updated
    ↓ Uvicorn --reload detects change
Container restarts uvicorn worker
    ↓
API available with updated code
```

```
Developer edits ./frontend/src/App.tsx (host)
    ↓ Bind mount sync
Container /app/src/App.tsx updated
    ↓ Vite file watcher (polling) detects change
Container triggers HMR
    ↓ WebSocket to browser
Browser hot-replaces module (no page reload)
```

### Database Initialization Flow
```
docker compose up
    ↓
db service starts
    ↓ Health check loop (5s interval)
PostgreSQL ready (pg_isready succeeds)
    ↓ depends_on:service_healthy
backend service starts
    ↓ entrypoint.sh
alembic upgrade head (run migrations)
    ↓
uvicorn starts (app ready)
```

---

## Constraints & Invariants

1. **Port Uniqueness**: Ports 5173, 8000, 5432 must not be in use on host
2. **Volume Permissions**: SQLite bind mount requires write permissions; container runs as root to avoid UID/GID issues
3. **Network Isolation**: Services communicate via service names within `app-network`; frontend uses `localhost:8000` in browser (host network)
4. **Platform Compatibility**: Images built for `linux/amd64` to ensure consistency across Intel and ARM (M1/M2) Macs
5. **Health Check Dependency**: Backend MUST wait for database health check before starting (prevents connection errors)
6. **Migration Idempotency**: Alembic migrations run on every backend startup; must be idempotent
7. **node_modules Isolation**: Frontend's `node_modules` MUST be a named volume (not bind mounted) for performance

---

## Entity Relationship Diagram

```
┌─────────────────┐
│   db Service    │
│  (postgres:15)  │
│   Port: 5432    │
│  Volume: pg_data│
└────────┬────────┘
         │ depends_on
         │ (health)
         ▼
┌─────────────────┐       ┌──────────────────┐
│ backend Service │       │ frontend Service │
│  (Python 3.12)  │       │   (Node 20)      │
│   Port: 8000    │       │   Port: 5173     │
│  Volume: src/   │       │  Volume: src/    │
│  Volume: ~/.db  │       │  Volume: n_m/    │
└─────────────────┘       └──────────────────┘
         │                         │
         └────────┬────────────────┘
                  │
           ┌──────▼───────┐
           │ app-network  │
           │   (bridge)   │
           └──────────────┘
```

Legend:
- `pg_data`: postgres_data named volume
- `n_m`: frontend_node_modules named volume
- `src/`: bind mounted source code
- `~/.db`: bind mounted SQLite directory
