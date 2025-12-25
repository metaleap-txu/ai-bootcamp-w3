# Implementation Plan: Docker Containerization & Orchestration

**Branch**: `002-docker-compose` | **Date**: December 25, 2025 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-docker-compose/spec.md`

## Summary

Containerize the full-stack database query tool application (FastAPI backend + React/Vite frontend + PostgreSQL database) using Docker and Docker Compose for orchestration. Provide development environment with hot-reload capabilities and a rebuild script for managing Docker images when dependencies change.

Primary technical approach:
- Multi-stage Dockerfiles for optimized development and production builds
- Docker Compose orchestration with service dependencies and networking
- Volume mounts for source code hot-reload during development
- Shell script for convenient image rebuilding workflow

## Technical Context

**Language/Version**: Python 3.12 (backend), Node.js 20+ (frontend), PostgreSQL 15 (database)
**Primary Dependencies**: Docker 24+, Docker Compose V2, FastAPI, React 18, Vite 5, uvicorn, npm
**Storage**: PostgreSQL (containerized), SQLite (host-mounted for persistence), Docker volumes
**Testing**: pytest (backend), vitest (frontend), Docker health checks
**Target Platform**: Linux containers (Dock
Primary technical approach:
- Multi-stage Dockerfiles for optimized development and production builds
- Docker Compose orchestration with service dependencies and networking
- Volume mounts for source code hot-reload during development
- Shell script for convenient image rebuilding workflow

## Tecinerized setup, must support M1/M2 Mac ARM architecture
**Scale/Scope**: 3 services (frontend, backend, database), 2 Dockerfiles, 1 docker-compose.yml, 1 rebuild script

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Security-First (NON-NEGOTIABLE)
- ✅ **PASS**: Containerization does not modify SQL validation or query restriction logic
- ✅ **PASS**: Database credentials remain encrypted in SQLite (host-mounted volume preserves encryption)
- ✅ **PASS**: No changes to security controls; containers execute existing secure code

### API-First Architecture
- ✅ **PASS**: Frontend-backend separation maintained via Docker networking
- ✅ **PASS**: Each service runs in isolated container with clear network boundaries
- ✅ **PASS**: API contracts unchanged; containerization is deployment concern only

### Test-First Development (NON-NEGOTIABLE)
- ✅ **PASS**: Existing tests will run in contai
## Tecinerized setup, must support M1/M2 Mac ARM archtend tests via `docker compose run --rm frontend npm test`
- ⚠️ **CLARIFICATION NEEDED**: Should Docker health checks be added as integration tests?

### Incremental Delivery via User Stories
- ✅ **PASS**: User stories are independently testable (P1: basic setup, P2: rebuild script, P3: cleanup)
- ✅ **PASS**: P1 delivers core value (working containerized environment)

### Developer Experience & Tooling
- ✅ **PASS**: Hot-reload preserved via volume mounts
- ✅ **PASS**: Development workflow improved (single command startup)
- ✅ **PASS**: Error messaging from Docker clearly indicates build/startup failures

**Overall**: ✅ PASS - No constitution violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/002-docker-compose/
├── plan.md              # This file (/speckit.plan command output)
├── rese- ✅ **PASS**: Existing tests will run inel.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
└── contracts/           # Phase 1 output (/speckit.plan command)
```

### Source Code (repository root)

```text
# Web application structure (existing)
backend/
├── Dockerfile           # NEW: Backend container image
├── src/
│   ├── models/
│   ├── services/
│   └── api/
├── tests/
└── pyproject.toml

frontend/
├── Dockerfile           # NEW: Frontend container image
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
├── tests/
└── package.json

# NEW: Docker orchestration
docker-compose.yml       # Service orchestration configuration
.dockerignore           # Files to exclude from Docker context

# NEW: Scripts
scripts├── plan.md       ontend and backend directories. Docker-related files added at repository root for orchestration, with individual Dockerfiles in each service directory for encapsulation.

## Complexity Tracking

No constitution violations requiring justification.

---

## Phase 0: Research & Discovery

*Purpose*: Resolve all technical unknowns before design begins.

### Research Tasks

#### R1: Docker Multi-Stage Build Patterns for Python/FastAPI
**Question**: What is the optimal Dockerfile structure for FastAPI with hot-reload in development and optimized production builds?

**Research Scope**:
- Multi-stage builds with base, development, and production stages
- Poetry vs pip vs pip-tools for dependency management in containers
- Hot-reloa│   └── servivicorn in Docker
- Layer caching strategies for Python dependencies
- Platform-specific builds (ARM64 for M1/M2 Macs, AMD64 for Intel/deployment)

**Deliverable**: Recommended Dockerfile structure with rationale

#### R2: Vite Development Server in Docker with Hot Module Replacement
**Question**: How to configure Vite dev server for proper HMR (Hot Module Replacement) when running in Docker?

**Research Scope**:
- Vite server configuration for Docker networking (host binding, WebSocket configuration)
- Volume mount strategies for node_modules (bind mount vs named volume)
- File watching issues in Docker and workarounds (polling vs native)
- Optimization for fast rebuilds and HMR performance

**Deliverable**: Vite configuration and Dockerfile approach for development

#### R3: Docker Compose Service Dependencies and Health Checks
**Question**: What is the best practice for ensuring database initialization completes before backend starts?

**Research Scope**:
- health check vs depends_on with condition:service_healthy
- PostgreSQL readiness detection strategies
- Alembic migrations in containerized environment (init containers vs entrypoint scripts)
- Network creation and service discovery in Docker Compose

**Deliverab**Question**: How to configure Vite dev server for proper HMR (Hot Mote Persistence Strategy in Containerized Environment
**Question**: How should SQLite database files be mounted to persist across container restarts while maintaining proper file permissions?

**Research Scope**:
- Bind mounts vs named volumes for SQLite files
- File permission issues (UID/GID mapping between host and container)
- Encryption key file persistence and security
- Backup and migration strategies

**Deliverable**: Volume mount strategy for SQLite and encryption keys

#### R5: Development vs Production Docker Configuration
**Question**: Should we use single Dockerfile with build args or separate Dockerfiles for dev vs prod?

**Research Scope**:
- docker-compose.yml vs docker-compose.override.yml for development overrides
- Environment variable management (.env files, ARG vs- Network creation and service discovery in Docker Compose

**Deliverab**Question**: HowDeliverable**: Configuration management approach

### Research Output Format

Each research task will be documented in `research.md` with:
```markdown
### [R#]: [Research Question]

**Decision**: [What was chosen]

**Rationale**: [Why this approach was selected]

**Alternatives Considered**:
- [Alternative 1]: [Why rejected]
- [Alternative 2]: [Why rejected]

**Implementation Notes**: [Specific configuration details, gotchas, etc.]
```

---

## Phase 1: Design & Contracts

*Prerequisites*: research.md completed with all NEEDS CLARIFICATION resolved

### Design Deliverables

#### D1: data-model.md
**Content**: Docker-specific data model
- Container image artifacts (name, tag, platform)
- Volume mappings (name, mount path, purpose)
- Network configuration (network name, port mappings)
- Service d- Environment variable management (.env files, ARG vs- Network creation and s per service

#### D2: contracts/dockerfile-backend.dockerfile
**Content**: Backend Dockerfile specification (commented template showing stages)

#### D3: contracts/dockerfile-frontend.dockerfile
**Content**: Frontend Dockerfile specification (commented template showing stages)

#### D4: contracts/docker-compose.schema.yaml
**Content**: Docker Compose service schema with all services, networks, volumes defined

#### D5: quickstart.md
**Content**: Developer quick-start guide
- Prerequisites (Docker installation, system requirements)
- First-time setup (`docker compose up`)
- Development workflow (making changes, viewing logs)
- Rebuilding images (`scripts/rebuild.sh`)
- Cleanup and reset commands
- Troubleshooting **Content**: Docker-sonflicts, permission errors)

### Agent Context Update

After design phase, run:
```bash
.specify/scripts/bash/update-agent-context.sh copilot
```

This will update `.github/copilot-instructions.md` with:
- Docker and Docker Compose as primary tools
- Container-based development workflow
- Service architecture (containerized frontend, backend, database)

---

## Phase 2: Task Planning

*NOT PART OF THIS COMMAND - See /speckit.tasks*

Task breakdown and implementation order will be defined by `/speckit.tasks` command after Phase 1 completes.

Expected task categories:
- Backend Dockerfile creation and optimization
- Frontend Dockerfile creation and HMR configuration
- Docker Compose orchestration setup
- Volume and network configuration
- rebuild.sh script implementation
- Documentation and quick-start guide
- Testing and validation

---

## Notes

- This plan focuses on development environment contai- Cleanup and reset commands
- Troubleshoof scope
- Existing application code remains unchanged; only deployment/orchestration files added
- Hot-reload is critical for developer experience; performance should match or exceed non-containerized setup
- Cross-platform compatibility (Intel/ARM Macs, Linux, Windows with WSL2) is a key constraint
