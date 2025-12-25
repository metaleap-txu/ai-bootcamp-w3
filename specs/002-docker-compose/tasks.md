# Tasks: Docker Containerization & Orchestration

**Input**: Design documents from `/specs/002-docker-compose/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Docker-specific file structure

- [ ] T001 Create scripts directory at repository root
- [ ] T002 [P] Create .dockerignore file at repository root to exclude unnecessary files from build context
- [ ] T003 [P] Verify backend/pyproject.toml and frontend/package.json are properly configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Docker infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create backend/entrypoint.sh script for migrations and uvicorn startup
- [ ] T005 [P] Update frontend/vite.config.ts with Docker-specific configuration (host: 0.0.0.0, polling, HMR)
- [ ] T006 [P] Create backend/.dockerignore for backend-specific exclusions
- [ ] T007 [P] Create frontend/.dockerignore for frontend-specific exclusions

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Development Environment Setup (Priority: P1) 🎯 MVP

**Goal**: Developers can start the entire application stack (frontend, backend, database) with a single command and have hot-reload working for both services

**Independent Test**: Run `docker compose up`, verify all services start successfully, make a code change in backend and frontend, verify hot-reload works within 5 seconds

### Implementation for User Story 1

- [ ] T008 [P] [US1] Create backend/Dockerfile with multi-stage build (base, dependencies, development stages)
- [ ] T009 [P] [US1] Create frontend/Dockerfile with development stage for Vite dev server
- [ ] T010 [US1] Create docker-compose.yml at repository root with all three services (db, backend, frontend)
- [ ] T011 [US1] Configure PostgreSQL service in docker-compose.yml with health check
- [ ] T012 [US1] Configure backend service in docker-compose.yml with depends_on (service_healthy), volumes, environment variables
- [ ] T013 [US1] Configure frontend service in docker-compose.yml with volumes (source code and named volume for node_modules)
- [ ] T014 [US1] Define app-network bridge network in docker-compose.yml
- [ ] T015 [US1] Define named volumes (postgres_data, frontend_node_modules) in docker-compose.yml
- [ ] T016 [US1] Make backend/entrypoint.sh executable and add shebang, database wait logic, migrations, and uvicorn startup
- [X] T017 [US1] Test full stack startup with `docker compose up` and verify all services reach healthy state
- [X] T018 [US1] Test backend hot-reload by modifying backend/src/main.py and verifying uvicorn reload
- [X] T019 [US1] Test frontend HMR by modifying frontend/src/App.tsx and verifying browser hot-reload

**Checkpoint**: At this point, User Story 1 should be fully functional - developers can run `docker compose up` and have a working development environment with hot-reload

---

## Phase 4: User Story 2 - Image Rebuilding (Priority: P2)

**Goal**: Developers have a convenient rebuild script to rebuild Docker images when dependencies change without remembering complex Docker commands

**Independent Test**: Modify package.json or pyproject.toml, run `scripts/rebuild.sh`, verify images are rebuilt successfully with clear progress messages

### Implementation for User Story 2

- [X] T020 [US2] Create scripts/rebuild.sh with color-coded output functions (print_info, print_success, print_error, print_warning)
- [X] T021 [US2] Implement main() function in scripts/rebuild.sh to parse service argument (backend|frontend|all)
- [X] T022 [US2] Implement rebuild_service() function with docker compose build --no-cache command
- [X] T023 [US2] Add Docker daemon check to scripts/rebuild.sh
- [X] T024 [US2] Add docker-compose.yml existence check to scripts/rebuild.sh
- [X] T025 [US2] Add usage help and error messages for invalid arguments
- [X] T026 [US2] Add success summary with next-step instructions in scripts/rebuild.sh
- [X] T027 [US2] Make scripts/rebuild.sh executable with chmod +x
- [X] T028 [US2] Test rebuild script with `./scripts/rebuild.sh` (all services)
- [X] T029 [US2] Test rebuild script with `./scripts/rebuild.sh backend` (backend only)
- [X] T030 [US2] Test rebuild script with `./scripts/rebuild.sh frontend` (frontend only)
- [X] T031 [US2] Test rebuild script error handling with Docker daemon stopped

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - developers can rebuild images conveniently when dependencies change

---

## Phase 5: User Story 3 - Clean Shutdown and Cleanup (Priority: P3)

**Goal**: Developers can stop all running containers and optionally clean up volumes/networks to free system resources or reset the development environment

**Independent Test**: Run `docker compose down` and verify graceful shutdown, run `docker compose down -v` and verify volumes are removed, restart with `docker compose up` and verify clean state

### Implementation for User Story 3

- [X] T032 [US3] Add restart policies (unless-stopped) to all services in docker-compose.yml
- [X] T033 [US3] Document shutdown commands in quickstart.md (already done - verification task)
- [X] T034 [US3] Test graceful shutdown with `docker compose down`
- [X] T035 [US3] Test shutdown with volume removal `docker compose down -v`
- [X] T036 [US3] Test restart after volume removal to verify fresh state

**Checkpoint**: All user stories should now be independently functional - full Docker development workflow is complete

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and final touches

- [X] T037 [P] Create .env.example file at repository root with OPENAI_API_KEY placeholder
- [X] T038 [P] Add README.md section about Docker setup (or update existing README)
- [X] T039 Verify quickstart.md instructions by following them step-by-step
- [X] T040 Test error scenarios documented in quickstart.md (port conflicts, Docker daemon not running)
- [X] T041 [P] Add health check to backend service in docker-compose.yml (optional enhancement)
- [X] T042 [P] Add health check to frontend service in docker-compose.yml (optional enhancement)
- [X] T043 Validate platform compatibility by testing on Intel and ARM (M1/M2) if possible
- [X] T044 Run full validation: `docker compose down -v && docker compose build --no-cache && docker compose up`
- [X] T045 Verify database persistence: create data, restart containers, verify data survives
- [X] T046 Verify SQLite persistence: use app to save connections, restart containers, verify data survives

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Must complete first (MVP - basic Docker setup)
  - User Story 2 (P2): Can start after US1; independent but enhances US1
  - User Story 3 (P3): Can start after US1; independent but complements US1
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Development Environment Setup**: 
  - Depends on: Foundational (Phase 2) complete
  - No dependencies on other user stories
  - This is the MVP - full containerized dev environment

- **User Story 2 (P2) - Image Rebuilding**: 
  - Depends on: US1 complete (needs docker-compose.yml to exist)
  - Independent: Can be tested by modifying dependencies and rebuilding

- **User Story 3 (P3) - Clean Shutdown and Cleanup**: 
  - Depends on: US1 complete (needs docker-compose.yml to exist)
  - Independent: Can be tested by starting services and shutting down

### Within Each User Story

#### User Story 1 (Development Environment Setup)
1. T008-T009 (Dockerfiles) can run in parallel - different files
2. T010 must complete before T011-T015 (compose config depends on base file)
3. T011-T013 (service configurations) can proceed sequentially (same file)
4. T014-T015 (networks/volumes) can proceed after services defined
5. T016 makes entrypoint.sh executable
6. T017-T019 are validation tests - run sequentially

#### User Story 2 (Image Rebuilding)
1. T020-T027 are sequential (building up the rebuild.sh script)
2. T028-T031 are validation tests - can run one after another

#### User Story 3 (Clean Shutdown and Cleanup)
1. T032-T033 are configuration updates
2. T034-T036 are validation tests - run sequentially

### Parallel Opportunities

#### Phase 1 - Setup
- T002 and T003 can run in parallel (different files)

#### Phase 2 - Foundational
- T005, T006, T007 can run in parallel (different files)
- T004 can run in parallel with others (different file)

#### User Story 1
- T008 and T009 (Dockerfiles) can run in parallel - different directories

#### Phase 6 - Polish
- T037, T038, T041, T042 can run in parallel (different files)

---

## Parallel Example: User Story 1

```bash
# Launch both Dockerfiles in parallel:
Task: "Create backend/Dockerfile with multi-stage build"
Task: "Create frontend/Dockerfile with development stage"

# Then create docker-compose.yml and configure services sequentially
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003) - ~5 minutes
2. Complete Phase 2: Foundational (T004-T007) - ~15 minutes
3. Complete Phase 3: User Story 1 (T008-T019) - ~60 minutes
4. **STOP and VALIDATE**: Test full Docker environment independently
5. **Deliverable**: Working containerized development environment with hot-reload

**MVP Success Criteria**:
- ✅ `docker compose up` starts all services in <3 minutes
- ✅ Frontend accessible at http://localhost:5173
- ✅ Backend accessible at http://localhost:8000
- ✅ Database accessible at localhost:5432
- ✅ Hot-reload works for backend (<5 seconds)
- ✅ HMR works for frontend (<5 seconds)

### Incremental Delivery

1. **Milestone 1**: Setup + Foundational → Foundation ready (~20 minutes)
2. **Milestone 2**: Add User Story 1 → Test independently → **MVP COMPLETE** (~80 minutes total)
3. **Milestone 3**: Add User Story 2 → Test independently → Rebuild script available (~100 minutes total)
4. **Milestone 4**: Add User Story 3 → Test independently → Cleanup features available (~110 minutes total)
5. **Milestone 5**: Polish → Documentation complete, all validation passed (~130 minutes total)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (~20 minutes)
2. **Once Foundational is done**:
   - Developer A: User Story 1 (Docker setup) - REQUIRED FIRST
3. **After US1 is complete**:
   - Developer B: User Story 2 (rebuild script) - Can start
   - Developer C: User Story 3 (cleanup features) - Can start
   - (US2 and US3 can proceed in parallel)
4. **All developers**: Phase 6 Polish together

**Note**: US1 must complete first as it creates the docker-compose.yml that US2 and US3 depend on.

---

## Task Count Summary

- **Phase 1 (Setup)**: 3 tasks
- **Phase 2 (Foundational)**: 4 tasks
- **Phase 3 (User Story 1 - P1)**: 12 tasks (8 implementation + 4 validation)
- **Phase 4 (User Story 2 - P2)**: 12 tasks (7 implementation + 5 validation)
- **Phase 5 (User Story 3 - P3)**: 5 tasks (2 implementation + 4 validation)
- **Phase 6 (Polish)**: 10 tasks
- **Total**: 46 tasks

### Breakdown by User Story

- **User Story 1**: 12 tasks (MVP - containerized development environment)
- **User Story 2**: 12 tasks (rebuild script convenience)
- **User Story 3**: 5 tasks (cleanup and shutdown)
- **Infrastructure**: 17 tasks (Setup + Foundational + Polish)

### Parallel Opportunities Identified

- Phase 1: 2 tasks can run in parallel
- Phase 2: 4 tasks can run in parallel
- User Story 1: 2 tasks can run in parallel (Dockerfiles)
- Phase 6: 4 tasks can run in parallel

### Independent Test Criteria

- **User Story 1**: `docker compose up` → all services start → hot-reload verified
- **User Story 2**: Modify dependencies → `scripts/rebuild.sh` → images rebuilt successfully
- **User Story 3**: `docker compose down -v` → volumes removed → clean restart works

### Suggested MVP Scope

**MVP = User Story 1 only** (Tasks T001-T019, 19 tasks total)

This delivers:
✅ Complete containerized development environment  
✅ Single-command startup (`docker compose up`)  
✅ Hot-reload for backend and frontend  
✅ All services orchestrated and networked properly  
✅ Database initialization and migrations  

This is a fully functional Docker setup. User Stories 2 and 3 are quality-of-life improvements.

---

## Format Validation

✅ All tasks follow checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`  
✅ All User Story tasks have [US1], [US2], or [US3] labels  
✅ Setup and Foundational tasks have NO story labels (shared infrastructure)  
✅ Polish tasks have NO story labels (cross-cutting)  
✅ Parallel tasks marked with [P]  
✅ File paths specified where applicable  
✅ Sequential task IDs (T001-T046)

---

## Notes

- No tests generated (not requested in specification)
- All tasks include exact file paths where applicable
- [P] tasks target different files and have no dependencies
- Each user story is independently testable per acceptance scenarios
- Commit after completing each user story phase
- Stop at any checkpoint to validate story independently
- US1 is MVP; US2 and US3 are enhancements but not required for basic Docker functionality
