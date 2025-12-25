# Tasks: Database Query Tool

**Input**: Design documents from `/specs/001-db-query-tool/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: NOT included - no TDD requirement specified in feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Web application structure: `backend/src/`, `frontend/src/`
Paths use web app conventions as specified in plan.md.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend directory structure: backend/src/{models,schemas,services,api,utils}, backend/tests/{contract,integration,unit}
- [X] T002 Create frontend directory structure: frontend/src/{components,pages,services,types,utils}, frontend/tests/{components,services}
- [X] T003 [P] Initialize Python project with pyproject.toml in backend/ (FastAPI 0.104+, Pydantic v2, sqlglot, OpenAI SDK, asyncpg, SQLAlchemy/SQLModel, pytest, httpx, ruff)
- [X] T004 [P] Initialize Node.js project with package.json in frontend/ (React 19, TypeScript 5.0+, Refine 5, Ant Design 5, Monaco Editor, Tailwind CSS 4, Vite, Vitest)
- [X] T005 [P] Configure backend linting/formatting: ruff.toml and mypy.ini in backend/
- [X] T006 [P] Configure frontend linting/formatting: .eslintrc.json, .prettierrc, tsconfig.json in frontend/
- [X] T007 [P] Create .gitignore entries for Python and Node.js artifacts
- [X] T008 [P] Setup SQLite database migrations framework (Alembic) in backend/alembic/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Create SQLite database schema in backend/alembic/versions/001_initial_schema.py (connections, metadata_cache, query_history tables per data-model.md)
- [X] T010 [P] Implement password encryption utilities in backend/src/utils/security.py (Fernet encryption/decryption, key management)
- [X] T011 [P] Implement SQLite session management in backend/src/utils/database.py (sessionmaker, get_db dependency)
- [X] T012 [P] Implement SQL validator using sqlglot in backend/src/utils/sql_validator.py (parse SQL, check SELECT-only, inject LIMIT 1000)
- [X] T013 Create FastAPI application entry point in backend/src/main.py (app instance, CORS middleware, health endpoint)
- [X] T014 Create backend configuration management in backend/src/config.py (environment variables, SQLite path, OpenAI API key)
- [X] T015 [P] Create base Pydantic schemas in backend/src/schemas/__init__.py (common response models, error response)
- [X] T016 [P] Setup Vite configuration in frontend/vite.config.ts (proxy to backend, build settings)
- [X] T017 [P] Create API client instance in frontend/src/services/api.ts (Axios with base URL, error interceptors)
- [X] T018 Setup Refine app structure in frontend/src/App.tsx (dataProvider, resources, routing)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and Test Database Connection (Priority: P1) 🎯 MVP

**Goal**: Users can add PostgreSQL connections, test them, and persist them in SQLite

**Independent Test**: User can add a connection, test it successfully, see it saved, and retrieve it on next app launch

### Implementation for User Story 1

- [X] T019 [P] [US1] Create Connection SQLAlchemy model in backend/src/models/connection.py
- [X] T020 [P] [US1] Create Connection Pydantic schemas in backend/src/schemas/connection.py (ConnectionCreate, ConnectionUpdate, ConnectionResponse)
- [X] T021 [US1] Implement ConnectionService in backend/src/services/connection_service.py (create, read, update, delete, test connection using asyncpg)
- [X] T022 [US1] Implement connections API endpoints in backend/src/api/connections.py (GET /api/connections, POST /api/connections, GET /api/connections/{id}, PUT /api/connections/{id}, DELETE /api/connections/{id}, POST /api/connections/{id}/test)
- [X] T023 [US1] Create Connection TypeScript types in frontend/src/types/connection.ts
- [X] T024 [US1] Implement connectionService in frontend/src/services/connectionService.ts (API calls for CRUD and test)
- [X] T025 [P] [US1] Create ConnectionForm component in frontend/src/components/ConnectionForm.tsx (form with validation, test button)
- [X] T026 [P] [US1] Create ConnectionList component in frontend/src/components/ConnectionList.tsx (display connections, edit/delete buttons)
- [X] T027 [US1] Create ConnectionsPage in frontend/src/pages/ConnectionsPage.tsx (integrate ConnectionForm and ConnectionList)
- [X] T028 [US1] Register connections resource in frontend/src/App.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 3 - Execute SQL Queries with Results Display (Priority: P1) 🎯 MVP

**Goal**: Users can write SELECT queries in Monaco Editor, execute them, and view results in a table

**Independent Test**: User can type a SELECT query, execute it, see results, and receive clear errors for invalid SQL

### Implementation for User Story 3

- [X] T029 [P] [US3] Create QueryHistory SQLAlchemy model in backend/src/models/query_history.py
- [X] T030 [P] [US3] Create Query Pydantic schemas in backend/src/schemas/query.py (QueryExecute, QueryResult, ValidationResult, QueryHistoryItem, ColumnMetadata)
- [X] T031 [US3] Implement QueryService in backend/src/services/query_service.py (validate_sql, execute_query with asyncpg, transform_sql with LIMIT injection, save to history)
- [X] T032 [US3] Implement queries API endpoints in backend/src/api/queries.py (POST /api/queries/execute, POST /api/queries/validate, GET /api/queries/history/{connection_id})
- [X] T033 [US3] Create Query TypeScript types in frontend/src/types/query.ts
- [X] T034 [US3] Implement queryService in frontend/src/services/queryService.ts (execute, validate, getHistory API calls)
- [X] T035 [US3] Create SqlEditor component in frontend/src/components/SqlEditor.tsx (Monaco Editor integration, syntax highlighting, Cmd+Enter keybinding, validation error markers)
- [X] T036 [US3] Create QueryResults component in frontend/src/components/QueryResults.tsx (Ant Design Table with pagination, column headers, NULL handling)
- [X] T037 [US3] Create QueryPage in frontend/src/pages/QueryPage.tsx (connection selector, SqlEditor, run button, QueryResults, execution time display)
- [X] T038 [US3] Add SQL validation error handling (display sqlglot errors with line numbers, reject non-SELECT statements, show LIMIT auto-apply message)
- [X] T039 [US3] Register queries resource in frontend/src/App.tsx

**Checkpoint**: At this point, User Stories 1 AND 3 should both work independently (MVP complete!)

---

## Phase 5: User Story 2 - Browse Database Metadata (Priority: P2)

**Goal**: Users can explore database schemas, tables, and columns with caching

**Independent Test**: User can expand schemas/tables, view column details, and see cached metadata load quickly

### Implementation for User Story 2

- [X] T040 [P] [US2] Create MetadataCache SQLAlchemy model in backend/src/models/metadata_cache.py
- [X] T041 [P] [US2] Create Metadata Pydantic schemas in backend/src/schemas/metadata.py (Schema, Table, Column, TableDetails, ForeignKey)
- [X] T042 [US2] Implement MetadataService in backend/src/services/metadata_service.py (fetch schemas/tables/columns from PostgreSQL via asyncpg, cache in SQLite with TTL, check cache expiration)
- [X] T043 [US2] Implement metadata API endpoints in backend/src/api/metadata.py (GET /api/metadata/{connection_id}/schemas, GET /api/metadata/{connection_id}/schemas/{schema_name}/tables, GET /api/metadata/{connection_id}/schemas/{schema_name}/tables/{table_name}/columns, POST /api/metadata/{connection_id}/refresh)
- [X] T044 [US2] Create Metadata TypeScript types in frontend/src/types/metadata.ts
- [X] T045 [US2] Implement metadataService in frontend/src/services/metadataService.ts (listSchemas, listTables, listColumns, refresh API calls)
- [X] T046 [US2] Create MetadataTree component in frontend/src/components/MetadataTree.tsx (Ant Design Tree, expandable schemas/tables/columns, refresh button, loading states)
- [X] T047 [US2] Add metadata browsing to QueryPage in frontend/src/pages/QueryPage.tsx (sidebar with MetadataTree, click to insert table/column names)
- [X] T048 [US2] Implement metadata cache invalidation logic (check expires_at, manual refresh button)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 5 - Export Query Results (Priority: P2)

**Goal**: Users can export query results to CSV, JSON, and Excel formats

**Independent Test**: User can execute a query and successfully download results in all three formats

### Implementation for User Story 5

- [X] T049 [P] [US5] Create Export Pydantic schemas in backend/src/schemas/export.py (ExportRequest)
- [X] T050 [US5] Implement ExportService in backend/src/services/export_service.py (export_to_csv using pandas, export_to_json using json, export_to_excel using pandas + openpyxl)
- [X] T051 [US5] Implement export API endpoints in backend/src/api/exports.py (POST /api/exports/csv, POST /api/exports/json, POST /api/exports/excel with proper Content-Disposition headers)
- [X] T052 [US5] Implement exportService in frontend/src/services/exportService.ts (exportCSV, exportJSON, exportExcel API calls with file download handling)
- [X] T053 [US5] Create ExportMenu component in frontend/src/components/ExportMenu.tsx (Ant Design Dropdown with CSV/JSON/Excel options)
- [X] T054 [US5] Add ExportMenu to QueryResults component in frontend/src/components/QueryResults.tsx (show only when results exist, pass query data)
- [X] T055 [US5] Handle file download in browser (trigger download with proper filename, handle large files)

**Checkpoint**: All P1 and P2 user stories complete (Enhanced version ready)

---

## Phase 7: User Story 4 - Natural Language to SQL (Priority: P3)

**Goal**: Users can generate SQL from natural language descriptions using OpenAI

**Independent Test**: User can type natural language, receive generated SQL with explanation, and execute it

### Implementation for User Story 4

- [X] T056 [P] [US4] Create NL2SQL Pydantic schemas in backend/src/schemas/nl2sql.py (NL2SQLRequest, NL2SQLResponse)
- [X] T057 [US4] Implement NL2SQLService in backend/src/services/nl2sql_service.py (fetch schema context from MetadataService, build prompt with schema, call OpenAI API, determine confidence level)
- [X] T058 [US4] Implement nl2sql API endpoint in backend/src/api/nl2sql.py (POST /api/nl2sql with OpenAI error handling)
- [X] T059 [US4] Create NL2SQL TypeScript types in frontend/src/types/nl2sql.ts
- [X] T060 [US4] Implement nl2sqlService in frontend/src/services/nl2sqlService.ts (generateSQL API call)
- [X] T061 [US4] Add NL2SQL tab to QueryPage in frontend/src/pages/QueryPage.tsx (natural language input, generate button, loading state, display explanation and warnings)
- [X] T062 [US4] Populate SqlEditor with generated SQL (allow editing before execution, show confidence level)
- [X] T063 [US4] Add OpenAI API key validation in backend/src/config.py (check environment variable, provide clear error if missing)

**Checkpoint**: All user stories (P1, P2, P3) complete (Full feature complete!)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T064 [P] Add comprehensive error handling in backend/src/api/*.py (convert exceptions to proper HTTP status codes, include error details)
- [X] T065 [P] Add loading states and error messages in all frontend components (spinners, error notifications, toast messages)
- [X] T066 [P] Implement SQL autocomplete in SqlEditor using Monaco (suggest table/column names from metadata cache)
- [X] T067 [P] Add data type formatting in QueryResults (format dates, numbers, booleans consistently)
- [X] T068 [P] Add connection status indicators (show last tested timestamp, green/red status badges)
- [X] T069 Update README.md with setup instructions, prerequisites, environment variables
- [X] T070 Run quickstart.md validation scenarios (validate all 5 user stories work end-to-end)
- [X] T071 Performance optimization (add query result pagination, optimize metadata cache queries, lazy load Monaco Editor)
- [X] T072 Security audit (verify password encryption, SQL injection prevention, CORS configuration)
- [X] T073 [P] Add documentation comments to all backend services and frontend components

**Final Checkpoint**: All 73 tasks complete! System ready for deployment ✅

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Can start after T018 ✅
- **User Story 3 (Phase 4)**: Depends on Foundational - Can start after T018 ✅
- **User Story 2 (Phase 5)**: Depends on Foundational + US1 (needs connections) - Can start after T028 ✅
- **User Story 5 (Phase 6)**: Depends on Foundational + US3 (needs query results) - Can start after T039 ✅
- **User Story 4 (Phase 7)**: Depends on Foundational + US2 (needs metadata for schema context) - Can start after T048 ✅
- **Polish (Phase 8)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - No dependencies on other stories ✅ MVP Component
- **User Story 3 (P1)**: Independent - No dependencies on other stories ✅ MVP Component
- **User Story 2 (P2)**: Requires US1 (connections) but independently testable
- **User Story 5 (P2)**: Requires US3 (query results) but independently testable
- **User Story 4 (P3)**: Requires US2 (metadata) but independently testable

### Within Each User Story

- Models before services
- Schemas before models/services (Pydantic schemas define contracts)
- Services before API endpoints
- Backend API before frontend services
- Frontend services before components
- Components before pages
- Core implementation before integration

### Parallel Opportunities

**Setup Phase (T001-T008)**:
- T003 (Python setup) || T004 (Node.js setup)
- T005 (Backend linting) || T006 (Frontend linting)
- T007 (gitignore) || T008 (Alembic)

**Foundational Phase (T009-T018)**:
- T010 (security utils) || T011 (database utils) || T012 (SQL validator)
- T015 (base schemas) || T016 (Vite config) || T017 (API client)

**User Story 1 (T019-T028)**:
- T019 (model) || T020 (schemas)
- T025 (ConnectionForm) || T026 (ConnectionList)

**User Story 3 (T029-T039)**:
- T029 (model) || T030 (schemas)
- T033 (types) can start immediately after T030

**User Story 2 (T040-T048)**:
- T040 (model) || T041 (schemas)

**User Story 5 (T049-T055)**:
- T049 (schemas) can start immediately

**User Story 4 (T056-T063)**:
- T056 (schemas) can start immediately

**Polish Phase (T064-T073)**:
- T064 (error handling) || T065 (loading states) || T066 (autocomplete) || T067 (formatting) || T068 (status indicators) || T073 (documentation)

---

## Parallel Example: MVP (User Stories 1 + 3)

After Foundational phase completes, two developers can work in parallel:

**Developer A - User Story 1 (T019-T028)**:
```bash
# Backend: Connection management
T019: Create Connection model
T020: Create Connection schemas
T021: Implement ConnectionService
T022: Implement connections API

# Frontend: Connection UI
T023: Create Connection types
T024: Implement connectionService
T025: Create ConnectionForm
T026: Create ConnectionList
T027: Create ConnectionsPage
T028: Register resource
```

**Developer B - User Story 3 (T029-T039)**:
```bash
# Backend: Query execution
T029: Create QueryHistory model
T030: Create Query schemas
T031: Implement QueryService
T032: Implement queries API

# Frontend: Query UI
T033: Create Query types
T034: Implement queryService
T035: Create SqlEditor
T036: Create QueryResults
T037: Create QueryPage
T038: Add validation errors
T039: Register resource
```

**Result**: MVP completed faster with parallel development!

---

## Implementation Strategy

### MVP First (User Stories 1 + 3 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T018) - CRITICAL checkpoint
3. Complete Phase 3: User Story 1 (T019-T028)
4. Complete Phase 4: User Story 3 (T029-T039)
5. **STOP and VALIDATE**: Test MVP independently using quickstart.md scenarios 1 and 3
6. Deploy/demo MVP if ready

**MVP delivers**: Connection management + SQL query execution (core value!)

### Incremental Delivery

1. **Foundation** (T001-T018) → Foundation ready ✅
2. **+ User Story 1** (T019-T028) → Can manage connections ✅
3. **+ User Story 3** (T029-T039) → Can execute queries ✅ **MVP!**
4. **+ User Story 2** (T040-T048) → Can browse metadata ✅
5. **+ User Story 5** (T049-T055) → Can export results ✅ **Enhanced!**
6. **+ User Story 4** (T056-T063) → Can use NL2SQL ✅ **Full Feature!**
7. **+ Polish** (T064-T073) → Production ready ✅

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers after Foundational phase:

**Sprint 1 (MVP)**:
- Developer A: User Story 1 (Connections)
- Developer B: User Story 3 (Queries)
- **Outcome**: MVP complete

**Sprint 2 (Enhanced)**:
- Developer A: User Story 2 (Metadata)
- Developer B: User Story 5 (Exports)
- **Outcome**: Enhanced version complete

**Sprint 3 (Full Feature)**:
- Developer A: User Story 4 (NL2SQL)
- Developer B: Polish tasks
- **Outcome**: Full feature complete

---

## Notes

- Tasks are organized by user story (US1, US2, US3, US4, US5) for independent development
- [P] tasks target different files with no dependencies - safe to parallelize
- Foundation (Phase 2) is CRITICAL - all stories blocked until T018 completes
- MVP = US1 + US3 (28% of total tasks, 100% of core value)
- Each user story tested independently per quickstart.md
- Verify Constitution compliance after each phase:
  - Security-First: T012 (SQL validator), T010 (password encryption)
  - API-First: All backend/src/api/*.py files
  - Test-First: Manual testing via quickstart.md (no automated tests requested)
  - Incremental Delivery: 5 independent user stories
  - Developer Experience: T035 (Monaco Editor), T066 (autocomplete)

---

**Total Tasks**: 73 tasks  
**MVP Tasks**: T001-T039 (39 tasks)  
**Enhanced Tasks**: T001-T055 (55 tasks)  
**Full Feature Tasks**: T001-T073 (73 tasks)

**Suggested Starting Point**: MVP (User Stories 1 + 3) - delivers maximum value with minimum effort!
