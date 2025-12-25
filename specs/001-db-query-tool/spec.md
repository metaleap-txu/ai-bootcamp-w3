# Feature Specification: Database Query Tool

**Feature Branch**: `001-db-query-tool`  
**Created**: 2025-12-25  
**Status**: Draft  
**Input**: Build a database query tool that allows users to add PostgreSQL database connections, view database metadata, execute SQL queries (SELECT only), and generate SQL from natural language. The system uses a FastAPI backend and a React + Refine frontend, with data stored locally in an SQLite database, and supports exporting query results.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add and Test Database Connection (Priority: P1) 🎯 MVP

Users need to securely add PostgreSQL database connections and verify they work before querying.

**Why this priority**: Without database connections, no other functionality is possible. This is the foundation.

**Independent Test**: User can add a PostgreSQL connection, test it successfully, see it saved in the connection list, and retrieve it on next app launch.

**Acceptance Scenarios**:

1. **Given** I am on the connections page, **When** I click "Add Connection" and fill in host, port, database, username, password, **Then** the connection is validated and saved to SQLite
2. **Given** I have entered connection details, **When** I click "Test Connection", **Then** I see a success message if connection works or error details if it fails
3. **Given** I have saved connections, **When** I close and reopen the app, **Then** I see all my saved connections in the list
4. **Given** I have a saved connection, **When** I click "Delete", **Then** the connection is removed from SQLite and the UI

---

### User Story 2 - Browse Database Metadata (Priority: P2)

Users need to explore database structure (schemas, tables, columns) to understand what data is available before writing queries.

**Why this priority**: Essential for query writing but depends on having connections working first.

**Independent Test**: User can select a connection, expand schemas/tables, view column details (name, type, nullable), and see the metadata cached for faster subsequent loads.

**Acceptance Scenarios**:

1. **Given** I have a valid connection, **When** I click "Browse Metadata", **Then** I see a tree view of schemas and tables
2. **Given** I am viewing the metadata tree, **When** I expand a table, **Then** I see all columns with their data types and constraints
3. **Given** I have browsed metadata once, **When** I browse again within 1 hour, **Then** the data loads from cache (<1 second)
4. **Given** I am viewing metadata, **When** I click "Refresh", **Then** the cache is invalidated and fresh metadata is fetched

---

### User Story 3 - Execute SQL Queries with Results Display (Priority: P1) 🎯 MVP

Users need to write and execute SELECT queries and view results in a tabular format.

**Why this priority**: Core value proposition - executing queries is the primary use case.

**Independent Test**: User can type a SELECT query in Monaco Editor, execute it, see results in a table, and receive clear error messages for invalid SQL or failed queries.

**Acceptance Scenarios**:

1. **Given** I have selected a connection, **When** I type a SELECT query in the editor and click "Run", **Then** I see results in a paginated table
2. **Given** my query doesn't specify a LIMIT, **When** I execute it, **Then** LIMIT 1000 is automatically applied
3. **Given** I try to execute UPDATE/DELETE/DROP, **When** I click "Run", **Then** I see an error "Only SELECT statements allowed"
4. **Given** my query has syntax errors, **When** I click "Run", **Then** I see validation errors before execution with line numbers
5. **Given** I have query results, **When** I scroll through the table, **Then** pagination works smoothly with 100 rows per page

---

### User Story 4 - Natural Language to SQL (Priority: P3)

Users want to describe queries in natural language and have them converted to SQL automatically.

**Why this priority**: Nice-to-have feature that enhances usability but not essential for core functionality.

**Independent Test**: User can type "show all users created in the last 7 days" and receive a valid SELECT query they can review and execute.

**Acceptance Scenarios**:

1. **Given** I have selected a connection and browsed metadata, **When** I type a natural language query and click "Generate SQL", **Then** I receive a SELECT query using actual table/column names
2. **Given** I have generated SQL, **When** I review it in the editor, **Then** I can edit it before executing
3. **Given** the natural language is ambiguous, **When** I click "Generate SQL", **Then** I see helpful error messages suggesting clarifications
4. **Given** NL2SQL generation takes time, **When** I click "Generate SQL", **Then** I see a loading indicator and can cancel if needed

---

### User Story 5 - Export Query Results (Priority: P2)

Users need to export query results for analysis in spreadsheets or other tools.

**Why this priority**: Common workflow need but not blocking for basic query execution.

**Independent Test**: User can execute a query and export results to CSV, JSON, or Excel format.

**Acceptance Scenarios**:

1. **Given** I have query results displayed, **When** I click "Export as CSV", **Then** a CSV file downloads with all visible columns
2. **Given** I have query results displayed, **When** I click "Export as JSON", **Then** a JSON file downloads with array of row objects
3. **Given** I have query results displayed, **When** I click "Export as Excel", **Then** an XLSX file downloads with formatted headers
4. **Given** I have a large result set (1000 rows), **When** I export, **Then** all rows are included (not just current page)

---

### Edge Cases

- What happens when a connection times out during query execution?
- How does the system handle very wide tables (100+ columns) in the results view?
- What if the PostgreSQL server is unreachable when browsing metadata?
- How are SQL syntax errors differentiated from database execution errors?
- What happens if the SQLite database file is corrupted or locked?
- How does the system handle special characters in table/column names (spaces, quotes, unicode)?
- What if a query returns 0 rows?
- How are NULL values displayed in the results table?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST validate and store PostgreSQL connection strings in local SQLite database (~/.db_query/db_query.db)
- **FR-002**: System MUST test database connections before saving and show clear success/failure messages
- **FR-003**: System MUST fetch and display database metadata (schemas, tables, columns, data types) with caching
- **FR-004**: System MUST parse SQL queries using sqlglot and reject non-SELECT statements
- **FR-005**: System MUST automatically apply LIMIT 1000 to queries without explicit LIMIT clause
- **FR-006**: System MUST execute SELECT queries on user-selected PostgreSQL connections and return results
- **FR-007**: System MUST display query results in paginated table format with column headers and data types
- **FR-008**: System MUST provide SQL editor with syntax highlighting, autocomplete, and error detection (Monaco Editor)
- **FR-009**: System MUST convert natural language queries to SQL using OpenAI API with database schema context
- **FR-010**: System MUST export query results to CSV, JSON, and Excel formats
- **FR-011**: System MUST store last 50 queries in SQLite for history/reuse
- **FR-012**: System MUST handle up to 10 concurrent database connections
- **FR-013**: System MUST provide clear error messages for connection failures, SQL errors, and validation failures
- **FR-014**: System MUST cache metadata for up to 1 hour to improve performance
- **FR-015**: System MUST allow manual metadata refresh to invalidate cache

### Key Entities *(include if feature involves data)*

- **Connection**: Represents a PostgreSQL database connection with host, port, database name, username, encrypted password, and connection status
- **MetadataCache**: Stores database schema, table, and column information with timestamp for cache invalidation
- **Query**: Represents a SQL query with query text, connection ID, execution timestamp, result count, and execution status
- **QueryResult**: Contains result set data with column metadata (names, types) and row data (paginated)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add and test a PostgreSQL connection in under 30 seconds
- **SC-002**: Metadata for a typical database (100 tables) loads in under 5 seconds on first fetch
- **SC-003**: Cached metadata loads in under 1 second
- **SC-004**: Simple SELECT queries (<1000 rows) execute and display results in under 3 seconds
- **SC-005**: SQL validation rejects non-SELECT statements with clear error messages 100% of the time
- **SC-006**: Natural language to SQL conversion completes in under 10 seconds
- **SC-007**: UI interactions (button clicks, navigation) respond in under 100ms
- **SC-008**: System successfully handles 10 concurrent database connections without errors
- **SC-009**: Query results up to 10,000 rows display with pagination without performance degradation
- **SC-010**: Export functions successfully generate files for all supported formats (CSV, JSON, Excel)
