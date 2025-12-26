# Implementation Plan: Data Export Module

**Branch**: `003-data-export` | **Date**: December 25, 2025 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-data-export/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add data export functionality to enable users to export query results in CSV and JSON formats. The system will provide automatic export prompts after query execution, one-click "Run & Export" automation for saved queries, natural language export requests via AI assistant, and batch export capabilities. Exports must preserve data integrity, handle large datasets (up to 1M rows) through streaming, comply with format specifications (RFC 4180 for CSV, JSON standard), and provide progress indicators for long-running operations.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.3 (frontend)
**Primary Dependencies**: FastAPI, Pydantic, pandas (backend); React 18, Refine 5, Ant Design (frontend)  
**Storage**: SQLite for export preferences and history; PostgreSQL query results exported to files  
**Testing**: pytest + httpx (backend contract/integration tests), vitest + @testing-library/react (frontend)  
**Target Platform**: Web application (Linux/macOS server, modern browsers for frontend)  
**Project Type**: Web - separate backend (FastAPI) and frontend (React+Refine)  
**Performance Goals**: Export <3s for 1K rows, <30s for 100K rows; streaming for 1M+ rows; 95% success rate  
**Constraints**: <5 clicks for manual export, 1 click for automated; RFC 4180 CSV compliance; valid JSON output  
**Scale/Scope**: Support concurrent exports (queued per user); handle up to 1M rows; CSV/JSON formats initially

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Security-First ✅ PASS

- **SQL Validation**: Export feature reads from QueryResult (already validated by existing query execution flow)
- **Query Restriction**: Export does not execute queries; operates on existing query results only
- **Automatic Limits**: Exports respect existing 1000-row query limit; streaming for larger exports
- **Connection Isolation**: No new database connections required; uses existing connection management
- **Input Sanitization**: Export format selection (CSV/JSON enum), filenames sanitized to prevent path traversal

**Assessment**: Export feature maintains security posture by operating on already-validated query results.

### II. API-First Architecture ✅ PASS

- **Backend**: New FastAPI endpoints for export operations (`POST /api/exports/csv`, `POST /api/exports/json`, etc.)
- **Frontend**: React components for export UI (ExportMenu, progress indicators) consuming export API
- **Storage Separation**: Export preferences in SQLite; exported files generated on-demand (not persisted)
- **Contract-Driven**: OpenAPI contracts defined for all export endpoints before implementation
- **Stateless APIs**: Export endpoints stateless; accept query result reference, return file or download URL

**Assessment**: Clean API separation maintained; export module follows existing architectural patterns.

### III. Test-First Development ✅ PASS

- **Red-Green-Refactor**: Tests written first for each export format, streaming logic, error handling
- **Test Types Required**:
  - Contract Tests: Export API endpoints (status codes, response headers, file content validation)
  - Integration Tests: CSV/JSON formatting, special character escaping, streaming for large datasets
  - Security Tests: Filename sanitization, no path traversal, format injection prevention
- **Test Coverage**: Target 80% for export services, utilities (CSV formatter, JSON serializer, streaming)
- **User Approval**: Export test scenarios in spec.md acceptance criteria; ready for validation

**Assessment**: TDD approach applied to export functionality; comprehensive test coverage planned.

### IV. Incremental Delivery via User Stories ✅ PASS

- **Priority-Driven**: P1 (Quick Export MVP), P2 (Automation), P3 (Natural Language), P4 (Batch)
- **Independent Deployment**: P1 can deploy without P2-P4; each story independently testable
- **Vertical Slices**: Each story includes backend API, frontend UI, and data formatting
- **MVP Focus**: P1 delivers core export value (manual CSV/JSON export after query execution)
- **Story Validation**: Acceptance criteria defined per story with clear pass/fail tests

**Assessment**: User stories structured for incremental delivery; P1 is viable standalone MVP.

### V. Developer Experience & Tooling ✅ PASS

- **Monaco Editor**: No changes required; export operates on existing query results
- **Type Safety**: TypeScript for export UI components; Pydantic schemas for export API responses
- **API Documentation**: OpenAPI/Swagger auto-docs for export endpoints
- **Error Messaging**: Clear errors for export failures (file generation errors, format errors, streaming failures)
- **Export Capabilities**: THIS IS THE FEATURE - CSV, JSON export functionality

**Assessment**: Export module enhances existing tooling; maintains type safety and API documentation standards.

**Constitution Compliance**: ✅ ALL GATES PASSED - No violations, no complexity justification needed.

---

## Phase 0: Research Complete ✅

**Output**: [research.md](research.md)

**Findings**:
- CSV export: RFC 4180 standard using Python `csv` module
- JSON export: Standard `json` module with custom encoder for datetime/Decimal
- Streaming: FastAPI `StreamingResponse` with batch processing (1K rows/batch)
- File download: HTTP `Content-Disposition` headers, no server-side storage
- Natural language: OpenAI GPT-4 function calling with regex fallback
- Progress tracking: Server-Sent Events (SSE) via `EventSourceResponse`
- Preferences: SQLite table for user defaults

**All NEEDS CLARIFICATION resolved**: Technical context complete with specific libraries and approaches.

---

## Phase 1: Design & Contracts Complete ✅

**Outputs**:
- [data-model.md](data-model.md)
- [contracts/openapi.yaml](contracts/openapi.yaml)
- [quickstart.md](quickstart.md)
- [.github/agents/copilot-instructions.md](.github/agents/copilot-instructions.md) (updated)

**Data Model**:
- `ExportPreferences`: User default format, metadata inclusion, JSON/CSV options
- `ExportHistory`: Audit trail of exports (format, row count, status, execution time)
- `ExportRequest/Response`: Transient API payloads (not persisted)

**API Contracts**:
- `POST /api/exports/csv`: CSV export endpoint (direct download or streaming)
- `POST /api/exports/json`: JSON export endpoint (direct download or streaming)
- `GET /api/exports/stream/{export_id}`: SSE progress updates for large exports
- `GET /api/exports/download/{file_id}`: Download completed streaming export
- `GET /api/export-preferences`: Retrieve user preferences
- `PUT /api/export-preferences`: Update user preferences
- `GET /api/export-history`: Query export history

**Quickstart Guide**:
- API usage examples (curl, React components)
- Backend implementation patterns (CSV/JSON services, FastAPI endpoints)
- Common workflows (manual export, run & export, NL export, batch export)
- Testing examples (contract tests)

**Agent Context Updated**: Copilot instructions updated with Python 3.12, TypeScript 5.3, FastAPI, React 18, Refine 5, pandas, SQLite/PostgreSQL context.

**Re-Check Constitution After Phase 1**:

### I. Security-First ✅ PASS (Reconfirmed)
- No new security concerns introduced by design
- Export operates on validated query results only
- Filename sanitization prevents path traversal
- No modification of database data

### II. API-First Architecture ✅ PASS (Reconfirmed)
- Clean OpenAPI contract defined for all endpoints
- Backend/frontend separation maintained
- Stateless API design (export on-demand, no stored state)

### III. Test-First Development ✅ PASS (Reconfirmed)
- Contract tests defined in quickstart for all endpoints
- Integration tests planned for formatters and streaming
- Security tests planned for filename sanitization

### IV. Incremental Delivery ✅ PASS (Reconfirmed)
- P1 (Quick Export): Basic CSV/JSON with direct download
- P2 (Automation): Preferences + "Run & Export"
- P3 (Natural Language): AI-driven export commands
- P4 (Batch): Multi-query ZIP export
- Each phase independently deployable

### V. Developer Experience ✅ PASS (Reconfirmed)
- OpenAPI documentation auto-generated
- Type-safe schemas (Pydantic backend, TypeScript frontend)
- Clear error messages in API responses
- Export feature enhances existing tooling

**Final Constitution Compliance**: ✅ ALL GATES PASSED POST-DESIGN

---

## Phase 2: Task Breakdown (NOT DONE - Use `/speckit.tasks`)

**Status**: Phase 0 and Phase 1 complete. Implementation planning stopped as per `/speckit.plan` scope.

To generate detailed task breakdown, run:
```bash
/speckit.tasks
```

This will create [tasks.md](tasks.md) with TDD-driven implementation tasks for each user story.

## Project Structure

### Documentation (this feature)

```text
specs/003-data-export/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (format standards, best practices)
├── data-model.md        # Phase 1 output (ExportRequest, ExportPreferences entities)
├── quickstart.md        # Phase 1 output (export API usage, examples)
├── contracts/           # Phase 1 output (OpenAPI schemas for export endpoints)
│   ├── openapi.yaml     # Export API contract
│   └── schemas.json     # ExportRequest, ExportResponse schemas
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── export_request.py        # NEW: ExportRequest SQLAlchemy model
│   │   └── export_preferences.py    # NEW: ExportPreferences SQLAlchemy model
│   ├── services/
│   │   ├── export_service.py        # NEW: Core export orchestration
│   │   ├── csv_formatter.py         # NEW: CSV generation (RFC 4180 compliant)
│   │   ├── json_formatter.py        # NEW: JSON serialization
│   │   └── stream_exporter.py       # NEW: Streaming for large datasets
│   ├── api/
│   │   └── exports.py               # NEW: Export API endpoints
│   ├── schemas/
│   │   └── export.py                # NEW: Pydantic schemas for export requests/responses
│   └── utils/
│       └── filename_sanitizer.py    # NEW: Sanitize export filenames
└── tests/
    ├── contract/
    │   └── test_export_api.py       # NEW: Export endpoint contract tests
    ├── integration/
    │   ├── test_csv_export.py       # NEW: CSV generation integration tests
    │   ├── test_json_export.py      # NEW: JSON generation integration tests
    │   └── test_stream_export.py    # NEW: Streaming export tests
    └── unit/
        ├── test_csv_formatter.py    # NEW: CSV formatting unit tests
        ├── test_json_formatter.py   # NEW: JSON formatting unit tests
        └── test_filename_sanitizer.py # NEW: Filename sanitization tests

frontend/
├── src/
│   ├── components/
│   │   ├── ExportMenu.tsx           # EXISTING: Referenced in workspace structure
│   │   └── ExportProgress.tsx       # NEW: Progress indicator for exports
│   ├── pages/
│   │   └── QueryPage.tsx            # MODIFIED: Add export triggers
│   ├── services/
│   │   └── exportService.ts         # EXISTING: Referenced in workspace structure
│   └── types/
│       └── export.ts                # NEW: TypeScript types for export data
└── tests/
    ├── components/
    │   ├── test_ExportMenu.test.tsx # NEW: ExportMenu component tests
    │   └── test_ExportProgress.test.tsx # NEW: Progress component tests
    └── services/
        └── test_exportService.test.ts # NEW: Export service tests
```

**Structure Decision**: Web application structure (Option 2) selected. Backend handles export file generation and streaming; frontend provides UI for export triggers, format selection, and progress tracking. New files isolated in export-specific modules to minimize impact on existing codebase. Existing `ExportMenu.tsx` and `exportService.ts` already present in workspace - will enhance rather than create from scratch.

## Complexity Tracking

No Constitution violations detected. All complexity justifications are N/A.
