# Data Model: Data Export Module

**Feature**: Data Export Module  
**Phase**: 1 (Design & Contracts)  
**Date**: December 25, 2025

## Overview

This document defines the data entities, relationships, validation rules, and state transitions for the data export feature. The system extends existing SQLite storage with export-specific tables while generating export files on-demand without persistent storage.

---

## Entity Definitions

### 1. ExportPreferences

Stores user-specific export preferences to enable one-click "Run & Export" automation and reduce repeated format selections.

**Attributes**:
- `user_id` (integer, primary key): User identifier (or session ID if no authentication)
- `default_format` (enum, default 'csv'): Preferred export format ('csv' or 'json')
- `include_metadata` (boolean, default false): Whether to include query metadata (SQL text, execution time) in export
- `pretty_json` (boolean, default false): Whether to pretty-print JSON with indentation
- `csv_include_bom` (boolean, default false): Whether to include UTF-8 BOM for Excel compatibility
- `created_at` (datetime, auto): Timestamp when preferences were created
- `updated_at` (datetime, auto): Timestamp when preferences were last modified

**Relationships**:
- Associated with user/session (conceptual; actual user management out of scope for MVP)

**Validation Rules**:
- `default_format` must be one of: 'csv', 'json'
- `include_metadata`, `pretty_json`, `csv_include_bom` must be boolean
- Cannot have duplicate `user_id` entries (enforced by primary key)

**Default Values**:
```python
{
    "default_format": "csv",
    "include_metadata": False,
    "pretty_json": False,
    "csv_include_bom": False
}
```

**State Transitions**:
```
[No Preferences] → (First Export) → [Created with Defaults]
[Created with Defaults] → (User Updates) → [Updated]
[Updated] → (User Updates Again) → [Updated] (overwrite)
```

**Indexes**:
- Primary key on `user_id` (implicit)

---

### 2. ExportHistory

Audit trail of export operations for debugging, analytics, and user reference.

**Attributes**:
- `id` (integer, primary key): Unique export history identifier
- `user_id` (integer, nullable): User who triggered export
- `query_history_id` (integer, foreign key → QueryHistory.id, nullable): Reference to source query
- `format` (enum, required): Export format used ('csv', 'json')
- `row_count` (integer, required): Number of rows exported
- `file_size_bytes` (integer, nullable): Size of generated export file
- `status` (enum, required): Export outcome ('success', 'failed', 'cancelled')
- `error_message` (text, nullable): Error details if status is 'failed'
- `execution_time_ms` (integer, nullable): Time taken to generate export
- `exported_at` (datetime, auto): Timestamp when export was initiated
- `filename` (string, required): Generated filename (for user reference)

**Relationships**:
- References `QueryHistory` (many-to-one, optional - some exports may be from unsaved queries)

**Validation Rules**:
- `format` must be one of: 'csv', 'json'
- `status` must be one of: 'success', 'failed', 'cancelled'
- `row_count` must be non-negative
- `file_size_bytes` must be non-negative if set
- If `status` is 'failed', `error_message` must be non-null
- If `status` is 'success', `row_count` and `file_size_bytes` should be set

**State Transitions**:
```
[Export Requested] → (Initiate) → [Pending] (create record with status pending)
[Pending] → (Generation Success) → [Success] (update status, file_size, execution_time)
[Pending] → (Generation Failure) → [Failed] (update status, error_message)
[Pending] → (User Cancels) → [Cancelled] (update status)
```

**Retention Policy**:
- Keep most recent 100 export history entries per user
- Automatically delete older entries when limit exceeded
- Cleanup job runs daily or on export creation

**Indexes**:
- `idx_export_history_user_id` on `user_id` (for user export history queries)
- `idx_export_history_exported_at` on `exported_at DESC` (for recent exports)
- `idx_export_history_status` on `status` (for filtering failed exports)

---

### 3. ExportRequest (Transient - Request Payload Only)

Represents an export request from the user. This is NOT a database entity; it's the request payload for export API endpoints.

**Attributes** (Request Schema):
- `query_result_id` (integer, optional): ID of query history to export (if re-exporting saved query)
- `query_result` (object, optional): In-memory query result if not from history
  - `columns` (array of string): Column names
  - `rows` (array of dict): Row data
- `format` (enum, required): Export format ('csv', 'json')
- `options` (object, optional): Format-specific options
  - `pretty` (boolean): For JSON - pretty print with indentation
  - `include_bom` (boolean): For CSV - include UTF-8 BOM
  - `include_metadata` (boolean): Include query metadata in export
- `filename` (string, optional): Custom filename (will be sanitized)

**Validation Rules**:
- Must provide either `query_result_id` OR `query_result` (not both, not neither)
- `format` must be 'csv' or 'json'
- If `query_result` provided, must have non-empty `columns` and `rows` arrays
- `filename` if provided, must pass sanitization (alphanumeric, dash, underscore, period only)

---

### 4. ExportResponse (Transient - API Response Only)

Represents the response from an export operation. NOT a database entity; returned by export API endpoints.

**Attributes** (Response Schema):
- `status` (enum): 'success', 'failed', 'streaming'
- `download_url` (string, optional): URL to download export file (for small exports)
- `stream_url` (string, optional): SSE URL for streaming export progress (for large exports)
- `filename` (string): Generated filename
- `file_size_bytes` (integer, optional): Size of export file (if known)
- `row_count` (integer): Number of rows exported
- `format` (string): Export format used
- `error` (string, optional): Error message if status is 'failed'

**Success Response Example**:
```json
{
  "status": "success",
  "download_url": "/api/exports/download/abc123",
  "filename": "query_results_20251225_143022.csv",
  "file_size_bytes": 15360,
  "row_count": 150,
  "format": "csv"
}
```

**Streaming Response Example**:
```json
{
  "status": "streaming",
  "stream_url": "/api/exports/stream/def456",
  "filename": "large_export_20251225_143022.csv",
  "row_count": 150000,
  "format": "csv"
}
```

---

## Entity Relationships Diagram

```
┌──────────────────┐
│ ExportPreferences│
│──────────────────│
│ user_id (PK)     │
│ default_format   │
│ include_metadata │
│ pretty_json      │
│ csv_include_bom  │
│ created_at       │
│ updated_at       │
└──────────────────┘

┌──────────────────┐          ┌────────────────┐
│ ExportHistory    │          │ QueryHistory   │
│──────────────────│          │────────────────│
│ id (PK)          │          │ id (PK)        │
│ user_id          │          │ connection_id  │
│ query_history_id │─────────►│ sql_query      │
│ format           │   0..1   │ status         │
│ row_count        │          │ executed_at    │
│ file_size_bytes  │          └────────────────┘
│ status           │
│ error_message    │
│ execution_time_ms│
│ exported_at      │
│ filename         │
└──────────────────┘

Note: ExportRequest and ExportResponse are transient (not persisted)
```

---

## Validation Summary

### ExportPreferences Validation
- Format enum: 'csv' or 'json'
- All boolean flags must be true/false
- User ID unique (primary key)

### ExportHistory Validation
- Format enum: 'csv' or 'json'
- Status enum: 'success', 'failed', 'cancelled'
- Non-negative row count and file size
- Error message required if status is 'failed'
- Reference to QueryHistory must exist (if provided)

### ExportRequest Validation (API Level)
- Exactly one of query_result_id or query_result provided
- Format enum: 'csv' or 'json'
- Query result has columns and rows if provided
- Filename sanitization (no path traversal, special chars)

---

## Data Access Patterns

### High-Frequency Operations
1. **Get user export preferences** (every export operation)
   - Query: `SELECT * FROM export_preferences WHERE user_id = ?`
   - Index: Primary key on `user_id`

2. **Create export history entry** (every export)
   - Insert: `INSERT INTO export_history (...) VALUES (...)`
   - Index: Auto-increment primary key

3. **Recent export history** (user dashboard/history page)
   - Query: `SELECT * FROM export_history WHERE user_id = ? ORDER BY exported_at DESC LIMIT 20`
   - Index: `idx_export_history_user_id`, `idx_export_history_exported_at`

### Low-Frequency Operations
1. **Update export preferences** (user settings change)
2. **Cleanup old export history** (daily background job)
3. **Query failed exports for debugging** (admin/debugging)

---

## Migration Strategy

### Initial Schema

```sql
-- Create export_preferences table
CREATE TABLE export_preferences (
    user_id INTEGER PRIMARY KEY,
    default_format VARCHAR(10) DEFAULT 'csv' CHECK(default_format IN ('csv', 'json')),
    include_metadata BOOLEAN DEFAULT FALSE,
    pretty_json BOOLEAN DEFAULT FALSE,
    csv_include_bom BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create export_history table
CREATE TABLE export_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    query_history_id INTEGER,
    format VARCHAR(10) NOT NULL CHECK(format IN ('csv', 'json')),
    row_count INTEGER NOT NULL CHECK(row_count >= 0),
    file_size_bytes INTEGER CHECK(file_size_bytes >= 0),
    status VARCHAR(20) NOT NULL CHECK(status IN ('success', 'failed', 'cancelled')),
    error_message TEXT,
    execution_time_ms INTEGER CHECK(execution_time_ms >= 0),
    exported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    filename VARCHAR(255) NOT NULL,
    FOREIGN KEY (query_history_id) REFERENCES query_history(id) ON DELETE SET NULL
);

CREATE INDEX idx_export_history_user_id ON export_history(user_id);
CREATE INDEX idx_export_history_exported_at ON export_history(exported_at DESC);
CREATE INDEX idx_export_history_status ON export_history(status);

-- Trigger to update updated_at on export_preferences
CREATE TRIGGER update_export_preferences_timestamp
AFTER UPDATE ON export_preferences
FOR EACH ROW
BEGIN
    UPDATE export_preferences SET updated_at = CURRENT_TIMESTAMP WHERE user_id = NEW.user_id;
END;
```

### Migration Compatibility
- New tables are independent; no changes to existing Connection, MetadataCache, QueryHistory tables
- Foreign key to QueryHistory is optional (nullable) to support exporting ad-hoc query results
- Can be added incrementally without breaking existing functionality

---

## File Generation (Not Persisted)

Export files are generated on-demand and streamed to the user. They are NOT stored on the server filesystem.

**CSV File Structure**:
```
Header Row: Column names separated by commas
Data Rows: Values separated by commas, quoted as needed per RFC 4180
Optional Metadata Footer (if include_metadata=true):
  # Query: SELECT * FROM users
  # Executed: 2025-12-25 14:30:22
  # Rows: 150
```

**JSON File Structure**:
```json
{
  "metadata": {  // If include_metadata=true
    "query": "SELECT * FROM users",
    "executed_at": "2025-12-25T14:30:22",
    "row_count": 150
  },
  "results": [
    {"id": 1, "email": "alice@example.com", "created_at": "2025-12-01T10:30:00"},
    {"id": 2, "email": "bob@example.com", "created_at": "2025-12-02T14:15:00"}
  ]
}
```

**Filename Generation**:
- Pattern: `{prefix}_{timestamp}.{extension}`
- Prefix: Sanitized from query name or default "query_results"
- Timestamp: `YYYYMMDD_HHMMSS` format (e.g., `20251225_143022`)
- Extension: `csv` or `json`
- Example: `sales_report_20251225_143022.csv`

---

## Data Model Complete

All entities, relationships, validations, and state transitions defined. Ready to generate API contracts.
