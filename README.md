# Database Query Tool

A full-featured PostgreSQL query tool with natural language support, built with FastAPI and React.

## Features

✅ **Connection Management** - Add, edit, test, and delete PostgreSQL connections with encrypted password storage
✅ **Metadata Browsing** - Browse database schemas, tables, and columns with lazy loading and caching
✅ **Query Execution** - Execute SELECT queries with Monaco Editor, syntax highlighting, and validation
✅ **Export Results** - Export query results to CSV, JSON, or Excel formats
✅ **Natural Language to SQL** - Generate SQL queries from plain English descriptions using OpenAI GPT-4

## Prerequisites

- **Docker**: 24.0 or higher (with Docker Compose V2)
- **Docker Desktop**: Recommended for macOS and Windows
- **OpenAI API Key**: Required for Natural Language to SQL feature (optional for other features)

**OR** for local development without Docker:

- **Python**: 3.12 or higher
- **Node.js**: 18.0 or higher
- **PostgreSQL**: Access to one or more PostgreSQL databases (version 12+)

## Quick Start with Docker (Recommended)

The easiest way to get started is using Docker Compose:

```bash
# 1. Clone the repository
git clone <repository-url>
cd ai-bootcamp-w3

# 2. Create environment file with your OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Start all services (database, backend, frontend)
docker compose up -d

# 4. Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

That's it! The application is now running with hot-reload enabled for development.

### Docker Development Workflow

**Start services:**
```bash
docker compose up -d
```

**View logs:**
```bash
docker compose logs -f              # All services
docker compose logs -f backend      # Backend only
docker compose logs -f frontend     # Frontend only
```

**Stop services:**
```bash
docker compose down                 # Stop and remove containers
docker compose down -v              # Also remove volumes (fresh start)
```

**Rebuild images (when dependencies change):**
```bash
./scripts/rebuild.sh                # Rebuild all images
./scripts/rebuild.sh backend        # Rebuild backend only
./scripts/rebuild.sh frontend       # Frontend only
```

### Docker Services

The `docker-compose.yml` defines three services:

1. **db** - PostgreSQL 15 database for connection metadata
2. **backend** - FastAPI application (Python 3.12)
3. **frontend** - Vite dev server (Node 20)

All services include:
- Hot-reload for code changes (backend uvicorn --reload, frontend Vite HMR)
- Volume mounts for source code
- Health checks and dependency ordering
- Automatic restart policies

### Docker Troubleshooting

**Port conflicts:**
```bash
# Check what's using port 5432, 8000, or 5173
lsof -ti:5432  # PostgreSQL
lsof -ti:8000  # Backend
lsof -ti:5173  # Frontend

# Kill conflicting process (macOS/Linux)
lsof -ti:5432 | xargs kill -9
```

**Docker daemon not running:**
```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker

# Windows
# Start Docker Desktop from Start Menu
```

**Reset everything:**
```bash
docker compose down -v              # Remove all containers and volumes
docker system prune -af             # Clean up Docker system
docker compose up -d                # Fresh start
```

## Prerequisites

- **Python**: 3.12 or higher
- **Node.js**: 18.0 or higher
- **PostgreSQL**: Access to one or more PostgreSQL databases (version 12+)
- **OpenAI API Key**: Required for Natural Language to SQL feature (optional for other features)

## Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Required for NL2SQL feature (optional otherwise)
OPENAI_API_KEY=sk-your-api-key-here

# Optional: Model selection (default: gpt-4)
OPENAI_MODEL=gpt-4

# Optional: Database location (default: ~/.db_query/db_query.db)
DATABASE_URL=sqlite:///path/to/custom/location.db

# Optional: Encryption key (auto-generated if not provided)
ENCRYPTION_KEY=your-32-byte-base64-encoded-key
```

## Installation

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn src.main:app --reload
```

Backend will run at: `http://localhost:8000`
API docs available at: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Frontend will run at: `http://localhost:5173`

## Usage

### 1. Add a Database Connection

1. Navigate to the **Connections** page
2. Click **Add Connection**
3. Enter connection details:
   - Name: Friendly name for the connection
   - Host: PostgreSQL server hostname
   - Port: PostgreSQL port (default: 5432)
   - Database: Database name
   - Username: PostgreSQL username
   - Password: PostgreSQL password (encrypted in storage)
4. Click **Test Connection** to verify
5. Click **Save**

### 2. Browse Database Metadata

1. Navigate to the **Query** page
2. Select a connection from the dropdown
3. Use the metadata tree on the left sidebar to:
   - Expand schemas to view tables
   - Expand tables to view columns
   - Click any item to insert it into the SQL editor
   - View column types, primary keys, and foreign keys
   - See approximate row counts for tables

### 3. Execute SQL Queries

1. Write SQL in the Monaco Editor (SQL tab)
2. Use Cmd+Enter (Mac) or Ctrl+Enter (Windows/Linux) to execute
3. View results in the table below with:
   - Formatted dates, numbers, and booleans
   - NULL value indicators
   - Execution time and row count
4. Export results using the **Export Results** button (CSV/JSON/Excel)

### 4. Generate SQL from Natural Language

1. Navigate to the **Natural Language** tab
2. Enter a description in plain English:
   - Example: "Show me all users who registered in the last 30 days"
   - Example: "Find the top 10 products by revenue"
3. Click **Generate SQL**
4. Review the generated SQL, explanation, and confidence level
5. Edit if needed, then execute

## Project Structure

```
ai-bootcamp-w3/
├── backend/                  # FastAPI backend
│   ├── src/
│   │   ├── api/             # REST API endpoints
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Utilities (DB, security, validation)
│   │   ├── config.py        # Configuration
│   │   └── main.py          # FastAPI app
│   ├── alembic/             # Database migrations
│   ├── pyproject.toml       # Python dependencies
│   └── .env                 # Environment variables
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API clients
│   │   ├── types/           # TypeScript types
│   │   └── utils/           # Utilities
│   ├── package.json         # Node.js dependencies
│   └── vite.config.ts       # Vite configuration
└── specs/                    # Specification documents
    └── 001-db-query-tool/
        ├── spec.md          # Feature specification
        ├── plan.md          # Technical plan
        ├── tasks.md         # Implementation tasks
        └── contracts/       # API contracts
```

## Security

- **Password Encryption**: All database passwords are encrypted using Fernet symmetric encryption before storage
- **SELECT-Only Queries**: SQL validator prevents destructive operations (INSERT, UPDATE, DELETE, DROP)
- **Automatic LIMIT**: Queries without LIMIT are automatically capped at 1000 rows
- **SQL Injection Prevention**: Uses parameterized queries and SQLGlot parsing
- **Local Storage**: All data stored locally in SQLite (~/.db_query/db_query.db)
- **No Authentication**: This is a local development tool - not intended for shared/production use

## Performance Optimizations

- **Metadata Caching**: Database schema cached with 1-hour TTL
- **Lazy Loading**: Tree nodes load children only when expanded
- **Connection Pooling**: PostgreSQL connections reused via asyncpg
- **Query Result Pagination**: Large result sets paginated in the UI
- **Row Count Estimation**: Uses pg_class.reltuples for instant row counts

## Troubleshooting

### Backend won't start

- Check Python version: `python --version` (must be 3.12+)
- Verify virtual environment is activated
- Run migrations: `alembic upgrade head`
- Check port 8000 is available

### Frontend won't connect to backend

- Verify backend is running at http://localhost:8000
- Check CORS configuration in backend/src/main.py
- Clear browser cache and reload

### Connection test fails

- Verify PostgreSQL is accessible from your machine
- Check firewall rules for PostgreSQL port
- Verify credentials are correct
- Check PostgreSQL version (12+ required)

### NL2SQL not working

- Verify `OPENAI_API_KEY` is set in backend/.env
- Check OpenAI API key has sufficient credits
- Review OpenAI API rate limits
- Check console for specific error messages

## Development

### Running Tests

Backend:
```bash
cd backend
pytest
```

Frontend:
```bash
cd frontend
npm test
```

### Code Quality

Backend:
```bash
cd backend
mypy src/
ruff check src/
```

Frontend:
```bash
cd frontend
npm run lint
```

### Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## License

MIT License - see LICENSE file for details

## Support

For issues and feature requests, please open an issue on the project repository.
