# Implementation Plan: Database Query Tool

**Branch**: `001-db-query-tool` | **Date**: 2025-12-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-db-query-tool/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a secure database query tool for PostgreSQL with natural language support. Users can add connections, browse schemas/tables, execute SELECT-only queries with Monaco Editor, and export results (CSV/JSON/Excel). FastAPI backend validates SQL via sqlglot (auto-applies LIMIT 1000), stores metadata in local SQLite (~/.db_query/), and uses OpenAI for NL2SQL. React + Refine frontend with Ant Design provides the UI.

## Technical Context

**Language/Version**: Backend: Python 3.12+, Frontend: TypeScript 5.0+ (React 19+)  
**Primary Dependencies**: Backend: FastAPI 0.104+, Pydantic v2, sqlglot, OpenAI SDK, asyncpg, SQLAlchemy/SQLModel; Frontend: React 19, Refine 5, Ant Design 5, Monaco Editor, Tailwind CSS 4, Vite  
**Storage**: Local: SQLite (~/.db_query/db_query.db) for connections and metadata cache; Remote: PostgreSQL (user-provided) for query execution  
**Testing**: Backend: pytest, pytest-asyncio, httpx; Frontend: Vitest, React Testing Library  
**Target Platform**: Backend: Cross-platform (Linux/macOS/Windows), local web server; Frontend: Modern browsers (Chrome, Firefox, Safari, Edge)  
**Project Type**: Web application (frontend + backend)  
**Performance Goals**: Metadata fetch <5s (100 tables), Query execution <3s (<1000 rows), NL2SQL <10s, UI responsiveness <100ms  
**Constraints**: No authentication (local tool), SELECT-only queries, Auto LIMIT 1000, Local storage in ~/.db_query/, CORS allow all origins  
**Scale/Scope**: 5-10 concurrent connections, 1000 tables per DB cache, 50 query history, 10k rows UI display with pagination

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Security-First (NON-NEGOTIABLE)
- **SQL Validation**: sqlglot will parse and validate all SQL ✅
- **Query Restriction**: Backend enforces SELECT-only via sqlglot AST inspection ✅
- **Automatic Limits**: Middleware applies LIMIT 1000 if not specified ✅
- **Connection Isolation**: Each PostgreSQL connection validated separately ✅
- **Input Sanitization**: Pydantic v2 models validate all API inputs ✅

### ✅ II. API-First Architecture
- **Backend**: FastAPI REST API handles all database operations ✅
- **Frontend**: React + Refine consumes API only, no direct DB access ✅
- **Storage Separation**: SQLite for local metadata, PostgreSQL for remote queries ✅
- **Contract-Driven**: OpenAPI schema auto-generated from FastAPI ✅
- **Stateless APIs**: No server-side sessions, all state in SQLite or JWT ✅

### ✅ III. Test-First Development (NON-NEGOTIABLE)
- **Red-Green-Refactor**: All tests written before implementation ✅
- **Contract Tests**: All FastAPI endpoints tested with httpx ✅
- **Integration Tests**: SQL validation, NL2SQL, PostgreSQL connections ✅
- **Security Tests**: SQL injection prevention, query restriction enforcement ✅
- **Coverage Target**: 80% minimum for backend services ✅

### ✅ IV. Incremental Delivery via User Stories
- **P1 Stories**: US1 (Add Connection) + US3 (Execute Queries) = MVP ✅
- **P2 Stories**: US2 (Browse Metadata) + US5 (Export Results) = Enhanced ✅
- **P3 Stories**: US4 (NL2SQL) = Optional enhancement ✅
- **Independent Deployment**: Each story deliverable without dependencies ✅
- **Vertical Slices**: Each story includes frontend, backend, and data components ✅

### ✅ V. Developer Experience & Tooling
- **Monaco Editor**: SQL syntax highlighting and autocomplete ✅
- **Type Safety**: TypeScript frontend + Pydantic backend ✅
- **API Documentation**: FastAPI auto-generates OpenAPI/Swagger docs ✅
- **Error Messaging**: Clear error messages for all failure scenarios ✅
- **Export Capabilities**: CSV, JSON, Excel export implemented ✅

**GATE STATUS**: ✅ **PASS** - All constitution principles satisfied, no violations to justify

## Project Structure

### Documentation (this feature)

```text
specs/001-db-query-tool/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification with user stories
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── openapi.yaml     # FastAPI OpenAPI schema
│   └── schemas.json     # Pydantic model schemas
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Configuration management
│   ├── models/
│   │   ├── connection.py          # Connection SQLAlchemy model
│   │   ├── query_history.py       # Query history model
│   │   └── metadata_cache.py      # Metadata cache model
│   ├── schemas/
│   │   ├── connection.py          # Pydantic schemas for connections
│   │   ├── query.py               # Pydantic schemas for queries
│   │   ├── metadata.py            # Pydantic schemas for metadata
│   │   └── export.py              # Pydantic schemas for exports
│   ├── services/
│   │   ├── connection_service.py  # Connection CRUD and testing
│   │   ├── metadata_service.py    # Metadata fetch and cache
│   │   ├── query_service.py       # SQL validation and execution
│   │   ├── nl2sql_service.py      # Natural language to SQL
│   │   └── export_service.py      # Result export (CSV/JSON/Excel)
│   ├── api/
│   │   ├── connections.py         # Connection endpoints
│   │   ├── metadata.py            # Metadata endpoints
│   │   ├── queries.py             # Query execution endpoints
│   │   └── exports.py             # Export endpoints
│   └── utils/
│       ├── sql_validator.py       # sqlglot validation logic
│       ├── security.py            # Password encryption
│       └── database.py            # SQLite session management
├── tests/
│   ├── contract/
│   │   ├── test_connections_api.py
│   │   ├── test_metadata_api.py
│   │   ├── test_queries_api.py
│   │   └── test_exports_api.py
│   ├── integration/
│   │   ├── test_sql_validation.py
│   │   ├── test_pg_connection.py
│   │   ├── test_nl2sql.py
│   │   └── test_export_formats.py
│   └── unit/
│       ├── test_connection_service.py
│       ├── test_metadata_service.py
│       ├── test_query_service.py
│       └── test_export_service.py
├── requirements.txt
├── pyproject.toml
└── pytest.ini

frontend/
├── src/
│   ├── main.tsx                   # App entry point
│   ├── App.tsx                    # Main app component
│   ├── components/
│   │   ├── ConnectionForm.tsx     # Add/edit connection form
│   │   ├── ConnectionList.tsx     # Display connections
│   │   ├── MetadataTree.tsx       # Schema/table browser
│   │   ├── SqlEditor.tsx          # Monaco editor wrapper
│   │   ├── QueryResults.tsx       # Results table
│   │   └── ExportMenu.tsx         # Export dropdown
│   ├── pages/
│   │   ├── ConnectionsPage.tsx    # Connections management
│   │   ├── QueryPage.tsx          # Query execution
│   │   └── HistoryPage.tsx        # Query history
│   ├── services/
│   │   ├── api.ts                 # Axios instance
│   │   ├── connectionService.ts   # Connection API calls
│   │   ├── metadataService.ts     # Metadata API calls
│   │   ├── queryService.ts        # Query API calls
│   │   └── exportService.ts       # Export API calls
│   ├── types/
│   │   ├── connection.ts          # TypeScript types
│   │   ├── metadata.ts
│   │   ├── query.ts
│   │   └── export.ts
│   └── utils/
│       ├── formatters.ts          # Data formatting
│       └── validators.ts          # Client-side validation
├── tests/
│   ├── components/
│   │   ├── ConnectionForm.test.tsx
│   │   ├── SqlEditor.test.tsx
│   │   └── QueryResults.test.tsx
│   └── services/
│       ├── connectionService.test.ts
│       └── queryService.test.ts
├── package.json
├── tsconfig.json
├── vite.config.ts
└── vitest.config.ts
```

**Structure Decision**: Web application structure with separate backend/ and frontend/ directories. Backend uses standard FastAPI structure with models (SQLAlchemy), schemas (Pydantic), services (business logic), and api (routes). Frontend uses Refine conventions with components, pages, and services. This aligns with the Web Application option from the template and supports independent frontend/backend development and testing.

## Complexity Tracking

> **No violations - this section intentionally left empty**

The Constitution Check passed all gates without violations. No additional complexity justification required.
