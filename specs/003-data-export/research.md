# Research: Data Export Module

**Feature**: Data Export Module  
**Phase**: 0 (Outline & Research)  
**Date**: December 25, 2025

## Overview

This document consolidates research findings on CSV/JSON export standards, streaming techniques for large datasets, best practices for file generation in web applications, and AI-driven natural language export workflows.

---

## Research Areas

### 1. CSV Export Standards (RFC 4180)

**Decision**: Implement CSV export following RFC 4180 specification

**Rationale**:
- RFC 4180 is the de facto standard for CSV files, ensuring compatibility with Excel, Google Sheets, pandas, and other tools
- Provides clear rules for escaping special characters (quotes, commas, newlines)
- Widely supported across programming languages and platforms
- Python's `csv` module implements RFC 4180 by default

**RFC 4180 Key Requirements**:
1. **Line Terminator**: CRLF (`\r\n`) for maximum compatibility
2. **Field Separator**: Comma (`,`)
3. **Quoting Rules**:
   - Fields containing commas, quotes, or newlines MUST be enclosed in double quotes
   - Double quotes within fields MUST be escaped by doubling (`""`)
   - Example: `Hello "World"` → `"Hello ""World"""`
4. **Header Row**: First row should contain column names
5. **Character Encoding**: UTF-8 with BOM for Excel compatibility (optional)

**Implementation Choice**: Use Python's `csv.DictWriter` with `quoting=csv.QUOTE_MINIMAL`

**Alternatives Considered**:
- **Manual CSV generation**: Rejected due to high risk of escaping errors and RFC non-compliance
- **pandas DataFrame.to_csv()**: Considered but adds unnecessary dependency for simple CSV generation; reserved for large dataset streaming
- **Custom CSV library**: Rejected; standard library `csv` module is sufficient and battle-tested

**Example Implementation**:
```python
import csv
import io

def generate_csv(columns: list[str], rows: list[dict]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
```

---

### 2. JSON Export Standards

**Decision**: Generate JSON using Python's standard `json` module with proper serialization for database types

**Rationale**:
- JSON is a standard data interchange format with universal parser support
- Python's `json` module is highly optimized and handles Unicode correctly
- Provides clear serialization for common types (str, int, float, bool, None)
- Easy to validate output with JSON schema validators

**JSON Export Requirements**:
1. **Structure**: Array of objects (one object per row)
2. **Encoding**: UTF-8 (default for JSON)
3. **Date/Time Handling**: ISO 8601 format (`YYYY-MM-DDTHH:MM:SS`)
4. **Null Handling**: Use `null` for SQL NULL values
5. **Number Precision**: Preserve integer vs float distinction
6. **Pretty Printing**: Optional `indent=2` for readability (user preference)

**Type Serialization Mapping**:
| PostgreSQL Type | Python Type | JSON Type | Serialization |
|----------------|-------------|-----------|---------------|
| integer, bigint | int | number | Direct |
| numeric, decimal | Decimal | number | Convert to float or string (preserve precision) |
| varchar, text | str | string | Direct |
| boolean | bool | boolean | Direct |
| timestamp, date | datetime, date | string | ISO 8601 format |
| JSON, JSONB | dict/list | object/array | Direct (already JSON) |
| NULL | None | null | Direct |

**Implementation Choice**: Custom JSON encoder extending `json.JSONEncoder` for datetime/Decimal handling

**Alternatives Considered**:
- **pandas DataFrame.to_json()**: Rejected for same reasons as CSV (unnecessary dependency)
- **orjson library**: Faster but adds external dependency; standard library sufficient for current scale
- **Manual JSON formatting**: Rejected due to escaping complexity and error risk

**Example Implementation**:
```python
import json
from datetime import datetime, date
from decimal import Decimal

class ExportJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)  # Or str(obj) for precision preservation
        return super().default(obj)

def generate_json(rows: list[dict], pretty: bool = False) -> str:
    indent = 2 if pretty else None
    return json.dumps(rows, cls=ExportJSONEncoder, indent=indent, ensure_ascii=False)
```

---

### 3. Streaming for Large Datasets

**Decision**: Implement streaming export using FastAPI's `StreamingResponse` with chunk-based generation

**Rationale**:
- Large datasets (100K+ rows) cannot be loaded entirely into memory without risking OOM errors
- Streaming allows generating and sending file chunks progressively
- FastAPI's `StreamingResponse` handles HTTP chunked transfer encoding automatically
- Users receive data faster (begins downloading immediately vs waiting for full file generation)

**Streaming Approach**:
1. **Database Cursor**: Use asyncpg's cursor API to fetch rows in batches (e.g., 1000 rows/batch)
2. **Chunk Generation**: Generate CSV/JSON for each batch, yield as bytes
3. **HTTP Streaming**: Return `StreamingResponse` with generator function
4. **Memory Management**: Process one batch at a time; garbage collect after each yield

**Implementation Pattern**:
```python
from fastapi import StreamingResponse
import asyncpg

async def stream_csv_export(query_result_id: int):
    async def generate():
        # Fetch query result metadata (columns, connection info)
        # Re-execute query with cursor (or paginate saved results)
        async with connection.transaction():
            async for batch in cursor:
                csv_chunk = generate_csv_chunk(batch)
                yield csv_chunk.encode('utf-8')
    
    return StreamingResponse(
        generate(),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="export.csv"'}
    )
```

**Batch Size Tuning**:
- Small batches (100 rows): More frequent I/O, slower overall but lower memory
- Large batches (10,000 rows): Faster but higher memory usage
- **Recommended**: 1,000 rows/batch balances memory and performance

**Alternatives Considered**:
- **Full in-memory generation**: Rejected for large datasets (OOM risk)
- **Background job + file storage**: Rejected for simplicity; adds complexity (job queue, storage cleanup)
- **Pagination with client-side assembly**: Rejected; poor UX, multiple HTTP requests

---

### 4. File Generation and Download in Web Applications

**Decision**: Use FastAPI file responses with appropriate `Content-Disposition` headers for browser download

**Rationale**:
- Modern browsers handle file downloads via HTTP response headers
- `Content-Disposition: attachment` triggers browser download dialog
- `Content-Type` header ensures correct file association (CSV → spreadsheet apps, JSON → text editors)
- No server-side file storage required (reduced complexity, no cleanup jobs)

**HTTP Response Headers**:
```python
headers = {
    'Content-Disposition': f'attachment; filename="{sanitized_filename}"',
    'Content-Type': 'text/csv; charset=utf-8',  # or 'application/json'
    'Cache-Control': 'no-cache',  # Prevent caching of potentially sensitive data
}
```

**Filename Sanitization**:
- Remove path traversal characters (`/`, `\`, `..`)
- Limit to alphanumeric, dash, underscore, period
- Max length: 255 characters (filesystem limit)
- Include timestamp for uniqueness: `query_results_20251225_143022.csv`

**Browser Compatibility**:
- Modern browsers (Chrome, Firefox, Safari, Edge) support `Content-Disposition` attachment
- No JavaScript required for basic download (server-driven)
- Optional: JavaScript can show progress indicator via fetch API with progress events

**Alternatives Considered**:
- **Blob URLs in frontend**: Requires transferring entire file to frontend first; negates streaming benefits
- **Server-side file storage + URL**: Adds complexity (storage, cleanup, expiration); rejected for simplicity
- **Data URLs**: Limited to small files (~2MB); rejected for scalability

---

### 5. Natural Language Processing for Export Commands

**Decision**: Use OpenAI GPT-4 function calling to interpret natural language export requests

**Rationale**:
- GPT-4 excels at intent classification and parameter extraction from natural language
- Function calling provides structured output (export format, options) vs freeform text parsing
- Existing NL2SQL integration already uses OpenAI SDK; reuse authentication and patterns
- Fallback to keyword matching for offline/degraded scenarios

**NL Export Command Patterns**:
| User Input | Intent | Extracted Parameters |
|-----------|--------|---------------------|
| "export as CSV" | export | `{format: "csv"}` |
| "save this as spreadsheet" | export | `{format: "csv"}` (inferred) |
| "export to JSON" | export | `{format: "json"}` |
| "download results" | export | `{format: "csv"}` (default) |
| "export last query" | export | `{query_id: "last"}` |

**GPT-4 Function Definition**:
```json
{
  "name": "trigger_export",
  "description": "Export query results to a file format",
  "parameters": {
    "type": "object",
    "properties": {
      "format": {
        "type": "string",
        "enum": ["csv", "json"],
        "description": "Export file format"
      },
      "query_identifier": {
        "type": "string",
        "description": "Which query to export (current, last, or query ID)"
      }
    },
    "required": ["format"]
  }
}
```

**Fallback Strategy**:
- If OpenAI API unavailable: regex-based keyword matching (`/export.*csv/i`, `/export.*json/i`)
- If ambiguous: prompt user with options ("Did you mean CSV or JSON?")
- If no format detected: default to CSV with confirmation

**Alternatives Considered**:
- **Rule-based NLP (spaCy, NLTK)**: Rejected; requires manual pattern maintenance, lower accuracy
- **Regex-only parsing**: Rejected; insufficient for complex requests, low user satisfaction
- **No NL support**: Rejected; spec explicitly requires natural language interaction (P3 user story)

---

### 6. Progress Indicators for Long-Running Exports

**Decision**: Use WebSocket or Server-Sent Events (SSE) for real-time export progress updates

**Rationale**:
- Large exports (100K+ rows) take >10 seconds; users need feedback to prevent abandonment
- SSE is simpler than WebSocket for server-to-client updates (no bidirectional communication needed)
- FastAPI supports SSE via `EventSourceResponse`
- Frontend can display progress bar with estimated completion time

**SSE Implementation Pattern**:
```python
from fastapi import EventSourceResponse

async def export_with_progress(query_id: int):
    async def generate_progress():
        total_rows = get_total_row_count(query_id)
        processed = 0
        
        async for batch in fetch_batches(query_id):
            # Generate export chunk
            processed += len(batch)
            progress_pct = (processed / total_rows) * 100
            
            # Send progress event
            yield f"data: {json.dumps({'progress': progress_pct, 'processed': processed, 'total': total_rows})}\n\n"
        
        yield "data: {\"status\": \"complete\"}\n\n"
    
    return EventSourceResponse(generate_progress())
```

**Frontend Progress Display**:
- Ant Design `Progress` component for visual indicator
- Show "X of Y rows exported" text
- Estimated time remaining based on average row processing rate
- Cancellation button (abort export via separate API call)

**Alternatives Considered**:
- **Polling**: Rejected; inefficient, higher latency, more server load
- **No progress indicator**: Rejected; poor UX for large exports (spec requires progress for >2s exports)
- **WebSocket**: Overkill for one-way progress updates; SSE is simpler

---

### 7. Export Preferences Persistence

**Decision**: Store export preferences in SQLite `export_preferences` table per user

**Rationale**:
- Users have default format preferences (CSV vs JSON)
- Reduces clicks for repeated exports ("Run & Export" uses saved preference)
- Aligns with existing architecture (SQLite for local metadata)
- Simple key-value structure, no complex querying needed

**Preference Schema**:
```sql
CREATE TABLE export_preferences (
    user_id INTEGER PRIMARY KEY,  -- Or session_id if no user auth
    default_format VARCHAR(10) DEFAULT 'csv',  -- 'csv' or 'json'
    include_metadata BOOLEAN DEFAULT false,     -- Include query text in export
    pretty_json BOOLEAN DEFAULT false,          -- JSON indent for readability
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**API for Preferences**:
- `GET /api/export-preferences`: Retrieve current user preferences
- `PUT /api/export-preferences`: Update preferences
- Preferences auto-created with defaults on first export

**Alternatives Considered**:
- **Browser localStorage**: Rejected; not accessible to backend for "Run & Export" automation
- **No persistence**: Rejected; forces users to select format every time (violates UX goal)
- **Configuration file**: Rejected; not user-specific, no UI for modification

---

## Summary of Decisions

| Area | Decision | Key Library/Tool |
|------|----------|-----------------|
| CSV Export | RFC 4180 compliant via Python `csv` module | `csv.DictWriter` |
| JSON Export | Standard JSON with custom encoder | `json.JSONEncoder` |
| Large Dataset Handling | Streaming via FastAPI `StreamingResponse` | `asyncpg` cursors |
| File Download | HTTP headers (`Content-Disposition`) | FastAPI `Response` |
| Natural Language | GPT-4 function calling with regex fallback | OpenAI SDK |
| Progress Tracking | Server-Sent Events (SSE) | `EventSourceResponse` |
| Preferences Storage | SQLite table | SQLAlchemy |

---

## Technical Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Memory overflow with large exports | High | Use streaming; process in batches of 1K rows |
| CSV escaping errors causing data corruption | High | Use standard library `csv` module (RFC 4180 compliant) |
| Browser blocking automatic downloads | Medium | Provide manual download link fallback; clear user instructions |
| OpenAI API downtime affecting NL exports | Low | Regex-based keyword fallback for basic commands |
| Concurrent exports overwhelming server | Medium | Queue exports per user; limit to 2 concurrent per user |
| Special characters breaking filenames | Medium | Strict filename sanitization; whitelist alphanumeric + safe chars |

---

## Research Complete

All technical unknowns from Technical Context resolved. Ready to proceed to Phase 1 (Design & Contracts).
