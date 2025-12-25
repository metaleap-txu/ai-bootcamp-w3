# Quick Start Guide: Docker Containerized Development

**Feature**: Docker Containerization & Orchestration  
**Date**: December 25, 2025  
**For**: Developers setting up the containerized development environment

---

## Prerequisites

### Required Software

1. **Docker Desktop** (version 24.0 or higher)
   - **macOS**: Download from [docker.com](https://www.docker.com/products/docker-desktop/)
   - **Windows**: Docker Desktop with WSL 2 backend
   - **Linux**: Docker Engine + Docker Compose V2

2. **Verify Installation**:
   ```bash
   docker --version          # Should show 24.0+
   docker compose version    # Should show v2.x+
   ```

3. **System Requirements**:
   - **RAM**: Minimum 8GB, recommended 16GB
   - **Disk Space**: 10GB free for Docker images and volumes
   - **Ports**: 5173, 8000, 5432 must be available

### Optional: OpenAI API Key
For NL2SQL (Natural Language to SQL) features, you'll need an OpenAI API key.

Create a `.env` file in the repository root:
```bash
# .env
OPENAI_API_KEY=your_api_key_here
```

> **Note**: The `.env` file is gitignored and will not be committed.

---

## First-Time Setup

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd ai-bootcamp-w3
git checkout 002-docker-compose  # Switch to the feature branch
```

### 2. Start All Services

```bash
docker compose up
```

**What happens**:
- Downloads PostgreSQL, Python, and Node.js base images (first time only, ~1-2 minutes)
- Builds backend and frontend Docker images (~2-3 minutes)
- Starts database service and waits for health check
- Runs database migrations (Alembic)
- Starts backend service with hot-reload
- Starts frontend service with HMR (Hot Module Replacement)

**Expected output**:
```
[+] Running 4/4
 ✔ Network app-network           Created
 ✔ Container db-query-tool-db    Healthy
 ✔ Container db-query-tool-backend Started
 ✔ Container db-query-tool-frontend Started
```

### 3. Verify Services

Open your browser and check:

| Service | URL | Expected Result |
|---------|-----|-----------------|
| Frontend UI | http://localhost:5173 | React application loads |
| Backend API | http://localhost:8000/docs | FastAPI Swagger UI |
| Backend Health | http://localhost:8000/health | `{"status": "healthy"}` |

### 4. Stop Services

Press `Ctrl+C` in the terminal where `docker compose up` is running.

Or, to stop services running in detached mode:
```bash
docker compose down
```

---

## Daily Development Workflow

### Starting Your Day

```bash
# Start all services in detached mode (background)
docker compose up -d

# View logs from all services
docker compose logs -f

# Or view logs from a specific service
docker compose logs -f backend
docker compose logs -f frontend
```

### Making Code Changes

#### Backend Changes (Python)

1. Edit files in `./backend/src/`
2. Uvicorn automatically detects changes and reloads
3. Check terminal logs for reload confirmation:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   INFO:     Will watch for changes in these directories: ['/app']
   INFO:     Detected file change in 'main.py'
   INFO:     Shutting down
   INFO:     Application startup complete.
   ```
4. Refresh browser or make API request to test changes

#### Frontend Changes (TypeScript/React)

1. Edit files in `./frontend/src/`
2. Vite HMR automatically updates the browser
3. Check browser console for HMR confirmation:
   ```
   [vite] hot updated: /src/App.tsx
   ```
4. Changes appear instantly without page reload

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db

# Last 100 lines from backend
docker compose logs --tail=100 backend
```

### Stopping Services

```bash
# Stop and remove containers (preserves data volumes)
docker compose down

# Stop, remove containers, and DELETE ALL DATA (CAUTION!)
docker compose down -v
```

---

## Rebuilding Images

### When to Rebuild

Rebuild Docker images when:
- You modify `package.json` (frontend dependencies)
- You modify `pyproject.toml` (backend dependencies)
- You change `Dockerfile` configuration
- You encounter persistent caching issues

### Option 1: Using the Rebuild Script (Recommended)

```bash
# Rebuild both frontend and backend
./scripts/rebuild.sh

# Rebuild only backend
./scripts/rebuild.sh backend

# Rebuild only frontend
./scripts/rebuild.sh frontend
```

The script provides:
- Clear progress messages with color-coded output
- Error handling and reporting
- Automatic cache invalidation (`--no-cache`)
- Next-step instructions

### Option 2: Using Docker Compose Directly

```bash
# Rebuild all images
docker compose build --no-cache

# Rebuild specific service
docker compose build --no-cache backend
docker compose build --no-cache frontend

# Rebuild and restart services
docker compose up --build --force-recreate
```

### After Rebuilding

```bash
# Stop old containers
docker compose down

# Start with new images
docker compose up
```

---

## Running Tests

### Backend Tests (pytest)

```bash
# Run all backend tests
docker compose run --rm backend pytest

# Run specific test file
docker compose run --rm backend pytest tests/unit/test_nl2sql_service.py

# Run with coverage
docker compose run --rm backend pytest --cov=src --cov-report=term

# Run with verbose output
docker compose run --rm backend pytest -vv
```

### Frontend Tests (vitest)

```bash
# Run all frontend tests
docker compose run --rm frontend npm test

# Run tests in watch mode
docker compose run --rm frontend npm test -- --watch

# Run with coverage
docker compose run --rm frontend npm test -- --coverage
```

---

## Troubleshooting

### Problem: Port Already in Use

**Error**: `Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use`

**Solution**:
```bash
# Find process using the port
lsof -i :8000   # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or change the port in docker-compose.yml
# ports:
#   - "8001:8000"  # Use different host port
```

### Problem: Docker Daemon Not Running

**Error**: `Cannot connect to the Docker daemon`

**Solution**:
- **macOS**: Open Docker Desktop application
- **Windows**: Start Docker Desktop
- **Linux**: `sudo systemctl start docker`

### Problem: Database Connection Errors

**Error**: `FATAL: database "dbquery" does not exist`

**Solution**:
```bash
# Remove all containers and volumes (CAUTION: deletes data)
docker compose down -v

# Restart fresh
docker compose up
```

### Problem: Frontend Hot-Reload Not Working

**Symptoms**: Code changes don't appear in browser

**Solutions**:
1. Check that source directory is mounted:
   ```bash
   docker compose exec frontend ls -la /app/src
   ```

2. Verify Vite file watching is enabled:
   - Look for polling configuration in `vite.config.ts`
   - Ensure `CHOKIDAR_USEPOLLING=true` if on WSL2 (Windows)

3. Rebuild frontend image:
   ```bash
   ./scripts/rebuild.sh frontend
   docker compose up --force-recreate frontend
   ```

### Problem: Backend Hot-Reload Not Working

**Symptoms**: Python code changes don't take effect

**Solutions**:
1. Check uvicorn reload logs:
   ```bash
   docker compose logs backend | grep "Detected file change"
   ```

2. Verify source mount:
   ```bash
   docker compose exec backend ls -la /app/src
   ```

3. Restart backend service:
   ```bash
   docker compose restart backend
   ```

### Problem: Permission Errors with SQLite

**Error**: `PermissionError: [Errno 13] Permission denied: '/root/.db_query/db_query.db'`

**Solution**:
```bash
# Ensure host directory exists and is writable
mkdir -p ~/.db_query
chmod 755 ~/.db_query

# Remove and recreate containers
docker compose down
docker compose up
```

### Problem: Out of Disk Space

**Error**: `no space left on device`

**Solution**:
```bash
# Remove unused Docker resources
docker system prune -a --volumes

# Check Docker disk usage
docker system df

# Remove specific unused images
docker image prune -a

# Remove specific unused volumes
docker volume prune
```

### Problem: Slow Performance on macOS

**Symptoms**: File operations are slow, builds take forever

**Solutions**:
1. Ensure named volumes are used for `node_modules`:
   - Check `docker-compose.yml` has `frontend_node_modules:/app/node_modules`

2. Increase Docker Desktop resources:
   - Open Docker Desktop → Settings → Resources
   - Increase CPUs to 4+
   - Increase Memory to 8GB+

3. Enable VirtioFS (macOS 12.5+):
   - Docker Desktop → Settings → General
   - Enable "Use the new Virtualization framework"
   - Enable "VirtioFS accelerated directory sharing"

---

## Advanced Usage

### Accessing Container Shell

```bash
# Backend shell (Python environment)
docker compose exec backend /bin/bash

# Frontend shell (Node environment)
docker compose exec frontend /bin/bash

# Database shell (PostgreSQL)
docker compose exec db psql -U postgres -d dbquery
```

### Running Alembic Migrations Manually

```bash
# Generate new migration
docker compose exec backend alembic revision --autogenerate -m "Add new table"

# Apply migrations
docker compose exec backend alembic upgrade head

# Rollback one migration
docker compose exec backend alembic downgrade -1
```

### Inspecting Volumes

```bash
# List all volumes
docker volume ls

# Inspect specific volume
docker volume inspect ai-bootcamp-w3_postgres_data
docker volume inspect ai-bootcamp-w3_frontend_node_modules

# View SQLite database (on host)
ls -la ~/.db_query/
```

### Cleaning Up Everything (Nuclear Option)

```bash
# Stop all containers
docker compose down -v

# Remove all images
docker rmi db-query-tool-backend:dev db-query-tool-frontend:dev

# Remove all unused Docker resources
docker system prune -a --volumes

# Rebuild from scratch
docker compose build --no-cache
docker compose up
```

---

## Environment Variables Reference

### Backend Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DEBUG` | `true` | Enable FastAPI debug mode |
| `POSTGRES_HOST` | `db` | PostgreSQL hostname (service name) |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_USER` | `postgres` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password (dev only!) |
| `POSTGRES_DB` | `dbquery` | PostgreSQL database name |
| `OPENAI_API_KEY` | `""` | OpenAI API key for NL2SQL |

### Frontend Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL (browser) |

### Overriding Variables

Create a `.env` file in the repository root:
```bash
# .env
OPENAI_API_KEY=sk-...
POSTGRES_PASSWORD=super_secret_password
```

Or pass them directly:
```bash
OPENAI_API_KEY=sk-... docker compose up
```

---

## Next Steps

1. **Explore the Application**:
   - Open http://localhost:5173
   - Create a database connection
   - Run sample queries

2. **Read the Documentation**:
   - [Feature Specification](spec.md) - What this feature provides
   - [Implementation Plan](plan.md) - Technical architecture
   - [Data Model](data-model.md) - Docker entities and relationships

3. **Start Development**:
   - Make code changes in `./backend/src/` or `./frontend/src/`
   - Watch changes apply automatically via hot-reload/HMR
   - Write tests in `./backend/tests/` or `./frontend/tests/`

4. **Run the Full Test Suite**:
   ```bash
   # Backend tests
   docker compose run --rm backend pytest
   
   # Frontend tests
   docker compose run --rm frontend npm test
   ```

---

## Getting Help

- **Docker Issues**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Vite**: https://vitejs.dev/
- **Project Issues**: [GitHub Issues](repository-url/issues)

For questions specific to this Docker setup, consult:
- [contracts/](contracts/) - Docker configuration contracts
- [research.md](research.md) - Technical decision rationale
