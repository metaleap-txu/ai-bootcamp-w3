<!--
SYNC IMPACT REPORT
==================
Version Change: None → 1.0.0 (Initial Constitution)
Modified Principles: N/A (Initial creation)
Added Sections: All sections (initial creation)
Removed Sections: None

Templates Status:
✅ plan-template.md - Reviewed, aligned with Security-First and API-First principles
✅ spec-template.md - Reviewed, aligned with user story priority requirements
✅ tasks-template.md - Reviewed, aligned with TDD and incremental delivery principles

Follow-up TODOs: None
-->

# QueryCraft Constitution

## Core Principles

### I. Security-First (NON-NEGOTIABLE)

All database operations MUST enforce strict security controls:
- **SQL Validation**: All SQL statements MUST be parsed and validated using sqlglot before execution
- **Query Restriction**: Only SELECT statements are permitted; INSERT, UPDATE, DELETE, DROP, ALTER are explicitly forbidden
- **Automatic Limits**: All SELECT queries MUST enforce a maximum LIMIT of 1000 rows to prevent resource exhaustion
- **Connection Isolation**: Each PostgreSQL connection MUST be validated and isolated; credentials stored securely in local SQLite with encryption at rest
- **Input Sanitization**: All user inputs (natural language, SQL, connection strings) MUST be sanitized and validated

**Rationale**: Database query tools have inherent security risks. This principle ensures no data modification or destruction can occur, and prevents denial-of-service through unbounded queries.

### II. API-First Architecture

The system MUST maintain clear separation between frontend and backend:
- **Backend**: FastAPI-based REST API that handles all database connections, SQL execution, and NL2SQL transformation
- **Frontend**: React + Refine UI that consumes the API and provides user interface only
- **Storage Separation**: Local metadata (connections, query history) in SQLite; remote data querying via PostgreSQL connections
- **Contract-Driven**: All API endpoints MUST have explicit contracts defined before implementation
- **Stateless APIs**: Backend APIs MUST be stateless; all state persisted in SQLite or session tokens

**Rationale**: Clean separation enables independent development, testing, and deployment of frontend and backend. API contracts ensure reliability and enable parallel team development.

### III. Test-First Development (NON-NEGOTIABLE)

TDD is mandatory for all feature development:
- **Red-Green-Refactor**: Tests MUST be written first, verified to fail, then implementation proceeds
- **Test Types Required**:
  - **Contract Tests**: For all API endpoints (FastAPI routes)
  - **Integration Tests**: For SQL validation, NL2SQL transformation, PostgreSQL connection handling
  - **Security Tests**: For SQL injection prevention, query restriction enforcement, LIMIT enforcement
- **Test Coverage**: Minimum 80% code coverage for backend services
- **User Approval**: Test scenarios MUST be reviewed and approved before implementation begins

**Rationale**: Database tools require high reliability and security. TDD ensures all security controls work correctly and prevents regressions.

### IV. Incremental Delivery via User Stories

Features MUST be delivered as independently testable user stories:
- **Priority-Driven**: User stories prioritized as P1 (MVP), P2, P3, etc.
- **Independent Deployment**: Each user story MUST be completable and deployable independently
- **Vertical Slices**: Each story MUST include frontend, backend, and data layer components
- **MVP Focus**: P1 story is the minimum viable product; must deliver core value alone
- **Story Validation**: Each story MUST have clear acceptance criteria and independent test scenarios

**Rationale**: Incremental delivery reduces risk, enables faster feedback, and ensures each story provides tangible value without dependencies on future work.

### V. Developer Experience & Tooling

The system MUST optimize for developer productivity:
- **Monaco Editor**: SQL editing with syntax highlighting, autocomplete, and error detection
- **Type Safety**: TypeScript frontend for compile-time error detection
- **API Documentation**: Automatic OpenAPI/Swagger documentation for all FastAPI endpoints
- **Error Messaging**: Clear, actionable error messages for SQL validation failures, connection errors, and API failures
- **Export Capabilities**: Query results MUST be exportable in multiple formats (CSV, JSON, Excel)

**Rationale**: High-quality tooling reduces development friction, prevents errors, and improves maintainability.

## Technology Standards

### Required Stack

**Backend**:
- Python 3.12 or higher
- FastAPI for REST API framework
- sqlglot for SQL parsing and validation
- OpenAI SDK for natural language to SQL transformation
- SQLAlchemy for SQLite ORM
- psycopg3 for PostgreSQL connections

**Frontend**:
- React 18 with TypeScript
- Refine 5 for admin UI framework
- Ant Design for UI components
- Monaco Editor for SQL editing
- Axios or fetch for API communication

**Storage**:
- SQLite for local metadata (connections, query history, user preferences)
- PostgreSQL (remote) for user data querying

### Code Quality Standards

- **Linting**: Backend uses ruff or flake8; Frontend uses ESLint
- **Formatting**: Backend uses black; Frontend uses Prettier
- **Type Checking**: Backend uses mypy; Frontend uses TypeScript strict mode
- **Documentation**: All public APIs, functions, and components MUST have docstrings/JSDoc
- **Commit Messages**: Conventional Commits format (feat:, fix:, docs:, test:, refactor:)

## Development Workflow

### Feature Development Process

1. **Specification**: Create feature spec with prioritized user stories (use `.specify/templates/spec-template.md`)
2. **Planning**: Generate implementation plan with technical approach (use `.specify/templates/plan-template.md`)
3. **Test Design**: Write test scenarios for each user story, get user approval
4. **Implementation**: Follow TDD red-green-refactor cycle for each task
5. **Validation**: Verify all tests pass, security controls enforced, acceptance criteria met
6. **Documentation**: Update API docs, user guides, and quickstart as needed

### Quality Gates

Before ANY code merge:
- ✅ All tests passing (contract, integration, security)
- ✅ Code coverage ≥80% for backend
- ✅ Type checking passes (mypy, tsc)
- ✅ Linting passes (ruff, ESLint)
- ✅ Security validation: SQL restriction enforcement verified
- ✅ API contract compliance verified
- ✅ User story acceptance criteria met

### Branch Strategy

- **Feature Branches**: `###-feature-name` format (e.g., `001-add-connection-ui`)
- **Branch Lifecycle**: Create → Implement → Test → Review → Merge → Delete
- **Main Branch**: Always deployable, protected, requires PR approval

## Governance

### Amendment Process

1. Propose amendment with rationale, affected sections, and migration plan
2. Document impact on existing features and templates
3. Update version according to semantic versioning:
   - **MAJOR**: Breaking changes to principles, removed requirements
   - **MINOR**: New principles added, expanded requirements
   - **PATCH**: Clarifications, wording improvements, non-semantic changes
4. Update all templates in `.specify/templates/` to reflect changes
5. Communicate changes to all developers

### Compliance Review

- All feature specifications MUST pass Constitution Check (defined in plan-template.md)
- Violations MUST be documented with justification in Complexity Tracking section
- Simpler alternatives MUST be evaluated before accepting complexity
- Security principles (I. Security-First) CANNOT be waived under any circumstances

### Version Control

- Constitution changes trigger template updates across all `.specify/templates/*.md` files
- Version increment documented in Sync Impact Report
- Historical versions maintained in git history

**Version**: 1.0.0 | **Ratified**: 2025-12-25 | **Last Amended**: 2025-12-25
