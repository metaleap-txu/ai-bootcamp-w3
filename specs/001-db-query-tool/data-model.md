# Data Model: Database Query Tool

**Feature**: Database Query Tool  
**Phase**: 1 (Design & Contracts)  
**Date**: 2025-12-25

## Overview

This document defines the data entities, relationships, validation rules, and state transitions for the database query tool. The system uses SQLite for local metadata storage and PostgreSQL (remote) for query execution.

---

## Entity Definitions

### 1. Connection

Represents a PostgreSQL database connection configuration.

**Attributes**:
- `id` (integer, primary key): Unique connection identifier
- `name` (string, required, max 100 chars): User-friendly connection name
- `host` (string, required): PostgreSQL server hostname or IP
- `port` (integer, required, range 1-65535): PostgreSQL server port (default: 5432)
- `database` (string, required, max 100 chars): Database name
- `username` (string, required, max 100 chars): Database username
- `password_encrypted` (string, required): Fernet-encrypted password
- `ssl_mode` (enum, optional): SSL connection mode (disable, allow, prefer, require, verify-ca, verify-full)
- `created_at` (datetime, auto): Timestamp when connection was created
- `updated_at` (datetime, auto): Timestamp when connection was last modified
- `last_tested_at` (datetime, nullable): Last successful connection test timestamp
- `is_active` (boolean, default true): Whether connection is enabled

**Relationships**:
- Has many `MetadataCache` entries (one-to-many)
- Has many `QueryHistory` entries (one-to-many)

**Validation Rules**:
- `name` must be unique per user
- `host` cannot be empty or whitespace-only
- `port` must be between 1 and 65535
- `database`, `username`, `password_encrypted` cannot be empty
- `password_encrypted` must be valid Fernet ciphertext

**State Transitions**:
```
[New Connection] → (Save) → [Untested]
[Untested] → (Test Success) → [Tested & Active]
[Untested] → (Test Failure) → [Untested] (remains in DB, shows error)
[Tested & Active] → (Edit) → [Untested] (invalidate last_tested_at)
[Tested & Active] → (Disable) → [Inactive]
[Inactive] → (Enable) → [Tested & Active]
[Any State] → (Delete) → [Deleted] (cascade delete cache and history)
```

**Indexes**:
- `idx_connection_name` on `name` (for search)
- `idx_connection_active` on `is_active` (for filtering)

---

### 2. MetadataCache

Stores cached database schema metadata to avoid repeated queries to PostgreSQL.

**Attributes**:
- `id` (integer, primary key): Unique cache entry identifier
- `connection_id` (integer, foreign key → Connection.id): Associated connection
- `schema_name` (string, nullable): PostgreSQL schema name (e.g., "public")
- `table_name` (string, nullable): Table name (null for schema-level cache)
- `cache_type` (enum, required): Type of metadata (SCHEMA_LIST, TABLE_LIST, COLUMN_LIST)
- `cache_data` (JSON, required): Serialized metadata structure
- `cached_at` (datetime, auto): Timestamp when cache was created
- `expires_at` (datetime, auto): Expiration timestamp (cached_at + 1 hour)

**Relationships**:
- Belongs to one `Connection` (many-to-one)

**Validation Rules**:
- `connection_id` must reference existing connection
- `cache_type` must be one of: SCHEMA_LIST, TABLE_LIST, COLUMN_LIST
- `cache_data` must be valid JSON
- `expires_at` must be after `cached_at`

**Cache Data Structures**:

```json
// SCHEMA_LIST
{
  "schemas": [
    {"name": "public", "owner": "postgres"},
    {"name": "analytics", "owner": "analyst"}
  ]
}

// TABLE_LIST (for a specific schema)
{
  "schema": "public",
  "tables": [
    {"name": "users", "row_count": 1234, "size_bytes": 524288},
    {"name": "orders", "row_count": 5678, "size_bytes": 1048576}
  ]
}

// COLUMN_LIST (for a specific table)
{
  "schema": "public",
  "table": "users",
  "columns": [
    {"name": "id", "type": "integer", "nullable": false, "default": "nextval('users_id_seq')"},
    {"name": "email", "type": "varchar(255)", "nullable": false, "default": null},
    {"name": "created_at", "type": "timestamp", "nullable": false, "default": "now()"}
  ],
  "primary_keys": ["id"],
  "foreign_keys": [
    {"column": "role_id", "references_table": "roles", "references_column": "id"}
  ]
}
```

**State Transitions**:
```
[Not Cached] → (Fetch Metadata) → [Cached & Valid]
[Cached & Valid] → (Time passes) → [Expired]
[Expired] → (Fetch Metadata) → [Cached & Valid] (update cache_data and cached_at)
[Cached & Valid] → (Manual Refresh) → [Cached & Valid] (force update)
[Any State] → (Connection Deleted) → [Deleted] (cascade)
```

**Indexes**:
- `idx_cache_connection_id` on `connection_id`
- `idx_cache_type` on `cache_type`
- `idx_cache_expires` on `expires_at` (for cleanup queries)

---

### 3. QueryHistory

Stores recent query executions for user reference and replay.

**Attributes**:
- `id` (integer, primary key): Unique query history identifier
- `connection_id` (integer, foreign key → Connection.id): Connection used for query
- `sql_query` (text, required): Original SQL query text
- `transformed_sql` (text, required): SQL after sqlglot transformation (with LIMIT)
- `executed_at` (datetime, auto): Timestamp when query was executed
- `execution_time_ms` (integer, nullable): Query execution time in milliseconds
- `row_count` (integer, nullable): Number of rows returned (null if error)
- `status` (enum, required): Execution status (SUCCESS, ERROR, CANCELLED)
- `error_message` (text, nullable): Error details if status is ERROR

**Relationships**:
- Belongs to one `Connection` (many-to-one)

**Validation Rules**:
- `connection_id` must reference existing connection
- `sql_query` and `transformed_sql` cannot be empty
- `status` must be one of: SUCCESS, ERROR, CANCELLED
- If `status` is ERROR, `error_message` must be set
- If `status` is SUCCESS, `row_count` must be set
- `execution_time_ms` must be non-negative if set

**State Transitions**:
```
[Query Submitted] → (Validate) → [Validating]
[Validating] → (Validation Success) → [Executing]
[Validating] → (Validation Failure) → [ERROR] (save with error_message)
[Executing] → (Execution Success) → [SUCCESS] (save with row_count, execution_time_ms)
[Executing] → (Execution Failure) → [ERROR] (save with error_message)
[Executing] → (User Cancels) → [CANCELLED]
```

**Retention Policy**:
- Keep most recent 50 queries per connection
- Automatically delete older queries when limit exceeded

**Indexes**:
- `idx_history_connection_id` on `connection_id`
- `idx_history_executed_at` on `executed_at DESC` (for recent queries)
- `idx_history_status` on `status` (for filtering errors)

---

### 4. QueryResult (Transient Entity - Not Persisted)

Represents the result of a query execution. This entity is NOT stored in the database; it exists only in memory during API responses.

**Attributes**:
- `columns` (array of ColumnMetadata): Column definitions
- `rows` (array of objects): Query result rows
- `row_count` (integer): Total number of rows
- `execution_time_ms` (integer): Query execution time
- `has_more` (boolean): Whether more rows exist beyond LIMIT

**ColumnMetadata Structure**:
```typescript
{
  name: string,          // Column name
  type: string,          // PostgreSQL type (e.g., "integer", "varchar(255)")
  nullable: boolean,     // Whether column allows NULL
  python_type: string    // Python type (e.g., "int", "str", "datetime")
}
```

**Row Structure**:
```typescript
{
  [column_name: string]: any  // Column values (null for NULL, typed otherwise)
}
```

**Example**:
```json
{
  "columns": [
    {"name": "id", "type": "integer", "nullable": false, "python_type": "int"},
    {"name": "email", "type": "varchar(255)", "nullable": false, "python_type": "str"},
    {"name": "created_at", "type": "timestamp", "nullable": false, "python_type": "datetime"}
  ],
  "rows": [
    {"id": 1, "email": "alice@example.com", "created_at": "2025-12-01T10:30:00"},
    {"id": 2, "email": "bob@example.com", "created_at": "2025-12-02T14:15:00"}
  ],
  "row_count": 2,
  "execution_time_ms": 145,
  "has_more": false
}
```

---

## Entity Relationships Diagram

```
┌──────────────┐
│  Connection  │
│──────────────│
│ id (PK)      │
│ name         │
│ host         │
│ port         │
│ database     │
│ username     │
│ password_enc │
│ created_at   │
│ updated_at   │
│ is_active    │
└──────┬───────┘
       │
       │ 1:N
       ├─────────────────────┐
       │                     │
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│MetadataCache │      │QueryHistory  │
│──────────────│      │──────────────│
│ id (PK)      │      │ id (PK)      │
│ connection_id│◄─────│ connection_id│
│ schema_name  │      │ sql_query    │
│ table_name   │      │ transformed  │
│ cache_type   │      │ executed_at  │
│ cache_data   │      │ row_count    │
│ cached_at    │      │ status       │
│ expires_at   │      │ error_msg    │
└──────────────┘      └──────────────┘
```

---

## Validation Summary

### Connection Validation
- Name uniqueness (per user)
- Host/database/username not empty
- Port range 1-65535
- Password encryption valid

### MetadataCache Validation
- Connection must exist
- Cache type from enum
- Valid JSON structure
- Expiration after cached time

### QueryHistory Validation
- Connection must exist
- SQL query not empty
- Status from enum
- Error message if status=ERROR
- Row count if status=SUCCESS

---

## Data Access Patterns

### High-Frequency Operations
1. **List active connections** (every page load)
   - Query: `SELECT * FROM connections WHERE is_active = true ORDER BY name`
   - Index: `idx_connection_active`

2. **Get cached metadata** (every metadata browse)
   - Query: `SELECT * FROM metadata_cache WHERE connection_id = ? AND cache_type = ? AND expires_at > now()`
   - Index: `idx_cache_connection_id`, `idx_cache_expires`

3. **Recent query history** (every history page load)
   - Query: `SELECT * FROM query_history WHERE connection_id = ? ORDER BY executed_at DESC LIMIT 50`
   - Index: `idx_history_connection_id`, `idx_history_executed_at`

### Low-Frequency Operations
1. **Create/update connection** (user action)
2. **Delete connection** (user action, cascades to cache and history)
3. **Invalidate metadata cache** (manual refresh)

---

## Migration Strategy

### Initial Schema

```sql
-- Create connections table
CREATE TABLE connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL CHECK(port BETWEEN 1 AND 65535),
    database VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL,
    password_encrypted TEXT NOT NULL,
    ssl_mode VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_tested_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_connection_name ON connections(name);
CREATE INDEX idx_connection_active ON connections(is_active);

-- Create metadata_cache table
CREATE TABLE metadata_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    connection_id INTEGER NOT NULL,
    schema_name VARCHAR(100),
    table_name VARCHAR(100),
    cache_type VARCHAR(20) NOT NULL CHECK(cache_type IN ('SCHEMA_LIST', 'TABLE_LIST', 'COLUMN_LIST')),
    cache_data JSON NOT NULL,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (connection_id) REFERENCES connections(id) ON DELETE CASCADE
);

CREATE INDEX idx_cache_connection_id ON metadata_cache(connection_id);
CREATE INDEX idx_cache_type ON metadata_cache(cache_type);
CREATE INDEX idx_cache_expires ON metadata_cache(expires_at);

-- Create query_history table
CREATE TABLE query_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    connection_id INTEGER NOT NULL,
    sql_query TEXT NOT NULL,
    transformed_sql TEXT NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_time_ms INTEGER,
    row_count INTEGER,
    status VARCHAR(20) NOT NULL CHECK(status IN ('SUCCESS', 'ERROR', 'CANCELLED')),
    error_message TEXT,
    FOREIGN KEY (connection_id) REFERENCES connections(id) ON DELETE CASCADE
);

CREATE INDEX idx_history_connection_id ON query_history(connection_id);
CREATE INDEX idx_history_executed_at ON query_history(executed_at DESC);
CREATE INDEX idx_history_status ON query_history(status);
```

---

## Data Model Complete

All entities, relationships, validations, and state transitions defined. Ready to generate API contracts in Phase 1.
