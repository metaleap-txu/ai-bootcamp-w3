# Tasks: Data Export Module

**Input**: Design documents from `/specs/003-data-export/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are EXCLUDED from this breakdown. The focus is on implementation tasks only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create database migration for export_preferences table in backend/alembic/versions/002_export_preferences.py
- [X] T002 Create database migration for export_history table in backend/alembic/versions/003_export_history.py
- [X] T003 [P] Create ExportPreferences SQLAlchemy model in backend/src/models/export_preferences.py
- [X] T004 [P] Create ExportHistory SQLAlchemy model in backend/src/models/export_history.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 [P] Create Pydantic schemas for export requests in backend/src/schemas/export.py
- [X] T006 [P] Implement filename sanitization utility in backend/src/utils/filename_sanitizer.py
- [X] T007 [P] Create CSV formatter service with RFC 4180 compliance in backend/src/services/csv_formatter.py
- [X] T008 [P] Create JSON formatter service with custom encoder in backend/src/services/json_formatter.py
- [X] T009 Create base export service class in backend/src/services/export_service.py
- [X] T010 [P] Create TypeScript export types in frontend/src/types/export.ts
- [X] T011 Run Alembic migrations to create export tables: alembic upgrade head

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Quick Export After Query Execution (Priority: P1) 🎯 MVP

**Goal**: Enable users to manually export query results in CSV or JSON format with direct download for small datasets and streaming for large datasets

**Independent Test**: Execute a query, click export button, select format (CSV/JSON), verify downloaded file contains correct data with proper formatting

### Implementation for User Story 1

- [X] T012 [P] [US1] Implement CSV export endpoint POST /api/exports/csv in backend/src/api/exports.py
- [X] T013 [P] [US1] Implement JSON export endpoint POST /api/exports/json in backend/src/api/exports.py
- [X] T014 [US1] Add export size threshold logic (small vs large dataset routing) in backend/src/services/export_service.py
- [X] T015 [US1] Implement direct download response for small datasets (<10K rows) in backend/src/services/export_service.py
- [X] T016 [US1] Implement streaming response logic for large datasets (>10K rows) in backend/src/services/stream_exporter.py
- [X] T017 [US1] Create export history logging in backend/src/services/export_service.py
- [X] T018 [P] [US1] Enhance ExportMenu component with CSV/JSON format selection in frontend/src/components/ExportMenu.tsx
- [X] T019 [US1] Add export button triggers to QueryPage in frontend/src/pages/QueryPage.tsx
- [X] T020 [US1] Implement exportService.exportCsv() method in frontend/src/services/exportService.ts
- [X] T021 [US1] Implement exportService.exportJson() method in frontend/src/services/exportService.ts
- [X] T022 [US1] Add file download handling in frontend exportService for direct downloads
- [X] T023 [US1] Handle "No data to export" edge case in backend/src/api/exports.py
- [X] T024 [US1] Add error handling for export failures in frontend/src/components/ExportMenu.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional - users can export query results manually in CSV or JSON format

---

## Phase 4: User Story 2 - One-Click Query and Export Automation (Priority: P2)

**Goal**: Enable "Run & Export" automation that executes saved queries and automatically exports results using user's default format preference

**Independent Test**: Save a query, set export preference to JSON, click "Run & Export", verify query executes and JSON file downloads automatically without format prompt

### Implementation for User Story 2

- [ ] T025 [P] [US2] Implement GET /api/export-preferences endpoint in backend/src/api/exports.py
- [ ] T026 [P] [US2] Implement PUT /api/export-preferences endpoint in backend/src/api/exports.py
- [ ] T027 [US2] Create export preferences service in backend/src/services/export_preferences_service.py
- [ ] T028 [US2] Add default preference auto-creation logic (first export creates defaults)
- [ ] T029 [P] [US2] Create export preferences UI component in frontend/src/components/ExportPreferences.tsx
- [ ] T030 [US2] Add "Run & Export" button to QueryPage for saved queries in frontend/src/pages/QueryPage.tsx
- [ ] T031 [US2] Implement automated export workflow (execute query → auto export) in frontend/src/services/exportService.ts
- [ ] T032 [US2] Load user preferences on app init in frontend/src/services/exportService.ts
- [ ] T033 [US2] Apply default format from preferences in "Run & Export" workflow
- [ ] T034 [US2] Handle preference updates and persistence in frontend ExportPreferences component

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - manual export and automated "Run & Export"

---

## Phase 5: User Story 3 - Natural Language Export Requests (Priority: P3)

**Goal**: Enable users to trigger exports via natural language commands like "export as CSV" or "save this as spreadsheet" through AI assistant integration

**Independent Test**: Execute a query, type "export this as spreadsheet" in chat, verify AI interprets intent as CSV export and triggers download

### Implementation for User Story 3

- [ ] T035 [P] [US3] Create OpenAI function definition for export in backend/src/services/nl2sql_service.py (or new nl_export_service.py)
- [ ] T036 [US3] Implement natural language export intent parser in backend/src/services/nl_export_service.py
- [ ] T037 [US3] Add format inference logic (spreadsheet → CSV, data → JSON) in backend/src/services/nl_export_service.py
- [ ] T038 [US3] Create fallback regex-based keyword matching for offline mode
- [ ] T039 [P] [US3] Add natural language export UI in chat interface or QueryPage
- [ ] T040 [US3] Integrate NL export service with existing chat/AI assistant in frontend
- [ ] T041 [US3] Handle ambiguous requests with clarification prompts ("Did you mean CSV or JSON?")
- [ ] T042 [US3] Implement "export last query" command handling when no current results displayed
- [ ] T043 [US3] Add AI confirmation messages ("I'll export this as CSV for spreadsheet use")

**Checkpoint**: All core user stories (US1, US2, US3) should now be independently functional

---

## Phase 6: User Story 4 - Batch Export for Multiple Queries (Priority: P4)

**Goal**: Enable users to select multiple queries from history and export them as separate files in a single ZIP archive

**Independent Test**: Execute 3 queries, select all from history, click "Export All as ZIP", verify ZIP file contains 3 separate CSV/JSON files

### Implementation for User Story 4

- [ ] T044 [P] [US4] Implement POST /api/exports/batch endpoint in backend/src/api/exports.py
- [ ] T045 [US4] Create batch export service with ZIP file generation in backend/src/services/batch_export_service.py
- [ ] T046 [US4] Add logic to handle mixed format preferences in batch exports
- [ ] T047 [US4] Implement individual file generation for each query in batch
- [ ] T048 [US4] Handle empty query results in batch (skip or include empty file)
- [ ] T049 [P] [US4] Add query selection checkboxes to query history UI in frontend
- [ ] T050 [US4] Create "Export All" button for multi-select in frontend/src/pages/QueryPage.tsx or history page
- [ ] T051 [US4] Implement batch export request formatting in frontend/src/services/exportService.ts
- [ ] T052 [US4] Handle ZIP file download in frontend
- [ ] T053 [US4] Add format selection dialog for batch exports (single format vs individual)

**Checkpoint**: All user stories should now be independently functional including batch exports

---

## Phase 7: Streaming & Progress (Cross-Cutting for US1, US2, US4)

**Purpose**: Add streaming support and progress indicators for large exports across applicable user stories

- [ ] T054 [P] Implement GET /api/exports/stream/{export_id} SSE endpoint in backend/src/api/exports.py
- [ ] T055 [P] Implement GET /api/exports/download/{file_id} endpoint in backend/src/api/exports.py
- [ ] T056 Create streaming export service with progress tracking in backend/src/services/stream_exporter.py
- [ ] T057 Implement chunk-based CSV generation (1000 rows/batch) in backend/src/services/csv_formatter.py
- [ ] T058 Implement chunk-based JSON generation in backend/src/services/json_formatter.py
- [ ] T059 Add temporary file storage for completed streaming exports
- [ ] T060 Implement file expiration logic (1 hour TTL) for temporary exports
- [ ] T061 [P] Create ExportProgress component with progress bar in frontend/src/components/ExportProgress.tsx
- [ ] T062 Implement SSE client for progress updates in frontend/src/services/exportService.ts
- [ ] T063 Add progress modal to QueryPage for streaming exports in frontend/src/pages/QueryPage.tsx
- [ ] T064 Implement cancel export functionality in frontend
- [ ] T065 Add estimated time remaining calculation based on row processing rate

**Checkpoint**: Streaming and progress indicators working for all large exports

---

## Phase 8: Export History (Cross-Cutting Enhancement)

**Purpose**: Add export history tracking and display

- [ ] T066 [P] Implement GET /api/export-history endpoint with filtering in backend/src/api/exports.py
- [ ] T067 Create export history query service in backend/src/services/export_history_service.py
- [ ] T068 Add export history cleanup job (keep last 100 per user) in backend/src/services/export_history_service.py
- [ ] T069 [P] Create export history UI component in frontend/src/components/ExportHistory.tsx
- [ ] T070 Add export history page or section to QueryPage in frontend/src/pages/QueryPage.tsx
- [ ] T071 Implement history filtering by status (success/failed/cancelled)
- [ ] T072 Add re-export functionality (export again from history) in frontend

**Checkpoint**: Export history fully functional with tracking and display

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T073 [P] Add comprehensive error messages for all export failure scenarios
- [ ] T074 [P] Implement proper logging for export operations across all services
- [ ] T075 Add export rate limiting (prevent resource exhaustion) in backend
- [ ] T076 Implement concurrent export queueing per user
- [ ] T077 Add metadata footer to CSV exports (if include_metadata option enabled)
- [ ] T078 Add metadata object to JSON exports (if include_metadata option enabled)
- [ ] T079 Implement UTF-8 BOM for CSV exports (Excel compatibility) based on preference
- [ ] T080 Add CSV CRLF line terminator enforcement (RFC 4180)
- [ ] T081 Validate all special character escaping in CSV (quotes, commas, newlines)
- [ ] T082 Validate datetime serialization to ISO 8601 in JSON
- [ ] T083 Validate Decimal handling in JSON exports (precision preservation)
- [ ] T084 [P] Update OpenAPI documentation in specs/003-data-export/contracts/openapi.yaml
- [ ] T085 [P] Add export examples to quickstart.md validation
- [ ] T086 Performance testing for 1M row export (streaming validation)
- [ ] T087 Browser compatibility testing (Chrome, Firefox, Safari, Edge)
- [ ] T088 Verify file downloads work across all browsers
- [ ] T089 Code cleanup and refactoring across export services
- [ ] T090 Add inline documentation for all export functions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Streaming (Phase 7)**: Can start after US1 implementation - enhances US1, US2, US4
- **Export History (Phase 8)**: Can start after US1 - provides audit trail
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories ✅ INDEPENDENT
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Uses export logic from US1 but adds preferences layer ✅ INDEPENDENT
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses export endpoints from US1 via NL interface ✅ INDEPENDENT
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Uses export logic from US1 for batch processing ✅ INDEPENDENT

### Within Each User Story

- Models before services (T003, T004 before T009)
- Schemas before endpoints (T005 before T012, T013)
- Utilities before services (T006, T007, T008 before T009)
- Backend endpoints before frontend service calls (T012, T013 before T020, T021)
- Services before UI components (T020, T021 before T018, T019)
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T003, T004 can run in parallel (different model files)

**Foundational Phase (Phase 2)**:
- T005, T006, T007, T008, T010 can all run in parallel (different files, independent utilities)

**User Story 1 (Phase 3)**:
- T012, T013 can run in parallel (different endpoints in same file, minimal conflicts)
- T018, T020, T021 can run in parallel after T012, T013 complete (different files)

**User Story 2 (Phase 4)**:
- T025, T026, T029 can run in parallel (backend endpoints + frontend component)

**User Story 3 (Phase 5)**:
- T035, T039 can run in parallel (backend NL service + frontend UI)

**User Story 4 (Phase 6)**:
- T044, T049 can run in parallel (backend endpoint + frontend UI)

**Streaming Phase (Phase 7)**:
- T054, T055, T061 can run in parallel (endpoints + frontend component)

**Export History Phase (Phase 8)**:
- T066, T069 can run in parallel (endpoint + frontend component)

**Polish Phase (Phase 9)**:
- T073, T074, T084, T085 can all run in parallel (documentation, logging, error handling)

---

## Parallel Example: User Story 1

```bash
# After Foundational phase completes, launch in parallel:
Task T012: "Implement CSV export endpoint POST /api/exports/csv in backend/src/api/exports.py"
Task T013: "Implement JSON export endpoint POST /api/exports/json in backend/src/api/exports.py"

# Once T012, T013 complete, launch in parallel:
Task T018: "Enhance ExportMenu component in frontend/src/components/ExportMenu.tsx"
Task T020: "Implement exportService.exportCsv() in frontend/src/services/exportService.ts"
Task T021: "Implement exportService.exportJson() in frontend/src/services/exportService.ts"
```

---

## Parallel Example: All User Stories After Foundational

```bash
# Once Foundational (Phase 2) completes, if team has 4 developers:

Developer A → User Story 1 (Tasks T012-T024)
Developer B → User Story 2 (Tasks T025-T034)
Developer C → User Story 3 (Tasks T035-T043)
Developer D → User Story 4 (Tasks T044-T053)

# All stories progress in parallel, each independently testable
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T011) - CRITICAL
3. Complete Phase 3: User Story 1 (T012-T024)
4. **STOP and VALIDATE**: Test manual CSV/JSON export independently
5. Deploy/demo MVP

**MVP Scope**: Manual export of query results in CSV or JSON format with direct download for small datasets. This delivers core value without automation, NL, or batch features.

### Incremental Delivery

1. Complete Setup + Foundational (T001-T011) → Foundation ready
2. Add User Story 1 (T012-T024) → Test independently → **Deploy/Demo MVP** 🎯
3. Add Streaming (T054-T065) → Enhance US1 with large dataset support → Deploy/Demo
4. Add User Story 2 (T025-T034) → Test independently → Deploy/Demo (automation)
5. Add User Story 3 (T035-T043) → Test independently → Deploy/Demo (NL export)
6. Add User Story 4 (T044-T053) → Test independently → Deploy/Demo (batch export)
7. Add Export History (T066-T072) → Deploy/Demo (audit trail)
8. Polish (T073-T090) → Final release

### Parallel Team Strategy

With multiple developers:

1. **Together**: Complete Setup (Phase 1) + Foundational (Phase 2)
2. **Once Foundational done, split work**:
   - Developer A: User Story 1 (Phase 3)
   - Developer B: User Story 2 (Phase 4)
   - Developer C: User Story 3 (Phase 5)
   - Developer D: User Story 4 (Phase 6) OR Streaming (Phase 7)
3. **Integration**: Stories merge independently without conflicts
4. **Together**: Polish phase (Phase 9)

---

## Task Summary

- **Total Tasks**: 90 tasks
- **Setup**: 4 tasks
- **Foundational**: 7 tasks (BLOCKING)
- **User Story 1 (P1 - MVP)**: 13 tasks
- **User Story 2 (P2)**: 10 tasks
- **User Story 3 (P3)**: 9 tasks
- **User Story 4 (P4)**: 10 tasks
- **Streaming & Progress**: 12 tasks
- **Export History**: 7 tasks
- **Polish**: 18 tasks

**Parallel Tasks**: 28 tasks marked [P] can run in parallel within their phase

**Independent Stories**: All 4 user stories are independently testable

**Suggested MVP Scope**: Setup + Foundational + User Story 1 = 24 tasks for core export functionality

---

## Notes

- [P] tasks = different files or minimal conflicts, can run in parallel
- [US1], [US2], [US3], [US4] labels map tasks to user stories for traceability
- Each user story is independently completable and testable
- No tests included as not explicitly requested in specification
- Focus on implementation tasks with clear file paths
- Stop at any checkpoint to validate story independently
- Commit after each task or logical group of parallel tasks
- Foundational phase MUST complete before any user story work begins
- User stories can proceed in parallel once foundation is ready