# Quickstart Guide: Database Query Tool

**Feature**: Database Query Tool  
**Phase**: 1 (Design & Contracts)  
**Date**: 2025-12-25  
**Purpose**: Validate implementation by running end-to-end feature scenarios

---

## Prerequisites

### Backend Requirements
- Python 3.12 or higher
- pip or poetry for package management
- SQLite (included with Python)
- PostgreSQL database for testing (local or remote)

### Frontend Requirements
- Node.js 18+ and npm/yarn/pnpm
- Modern browser (Chrome, Firefox, Safari, Edge)

---

## Setup Instructions

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create local storage directory
mkdir -p ~/.db_query

# Generate encryption key (one-time)
python -c "from cryptography.fernet import Fernet; import os; key = Fernet.generate_key(); os.makedirs(os.path.expanduser('~/.db_query'), exist_ok=True); open(os.path.expanduser('~/.db_query/secret.key'), 'wb').write(key)"

# Run database migrations (creates SQLite database)
python -m alembic upgrade head

# Start FastAPI development server
uvicorn src.main:app --reload --port 8000
```

Backend should now be running at http://localhost:8000

API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install  # or: yarn install / pnpm install

# Start Vite development server
npm run dev  # or: yarn dev / pnpm dev
```

Frontend should now be running at http://localhost:5173

---

## End-to-End Validation Scenarios

### Scenario 1: Add and Test PostgreSQL Connection (P1)

**Goal**: Verify users can add a database connection and test it successfully.

**Steps**:
1. Open http://localhost:5173 in browser
2. Navigate to "Connections" page
3. Click "Add Connection" button
4. Fill in connection form:
   - Name: "Test DB"
   - Host: "localhost" (or your PostgreSQL host)
   - Port: 5432
   - Database: "postgres" (or your database name)
   - Username: "postgres" (or your username)
   - Password: [your password]
   - SSL Mode: "prefer"
5. Click "Test Connection" button
6. **Expected**: See success message with latency and server version
7. Click "Save" button
8. **Expected**: Connection appears in connections list
9. Refresh page
10. **Expected**: Connection still appears (persisted in SQLite)

**Validation Checklist**:
- [ ] Connection form validates required fields
- [ ] Test connection shows success/failure with clear message
- [ ] Password is encrypted in SQLite (check ~/.db_query/db_query.db)
- [ ] Connection persists across page reloads
- [ ] Can edit and delete connections

**API Endpoints Used**:
- `POST /api/connections` (create connection)
- `POST /api/connections/{id}/test` (test connection)
- `GET /api/connections` (list connections)

---

### Scenario 2: Browse Database Metadata (P2)

**Goal**: Verify users can explore database schemas, tables, and columns.

**Steps**:
1. From connections list, click "Browse Metadata" on a connection
2. **Expected**: See tree view with schemas (e.g., "public")
3. Expand a schema (e.g., "public")
4. **Expected**: See list of tables with row counts
5. Expand a table (e.g., "users")
6. **Expected**: See columns with names, types, nullable flags
7. **Expected**: See primary keys and foreign keys (if any)
8. Close and reopen metadata browser
9. **Expected**: Metadata loads quickly from cache (<1 second)
10. Click "Refresh" button
11. **Expected**: See loading indicator, then fresh metadata

**Validation Checklist**:
- [ ] Schemas load successfully
- [ ] Tables show row counts and sizes
- [ ] Columns display correct data types
- [ ] Primary keys and foreign keys are shown
- [ ] Metadata caches for 1 hour (check metadata_cache table)
- [ ] Manual refresh invalidates cache

**API Endpoints Used**:
- `GET /api/metadata/{connection_id}/schemas` (list schemas)
- `GET /api/metadata/{connection_id}/schemas/{schema}/tables` (list tables)
- `GET /api/metadata/{connection_id}/schemas/{schema}/tables/{table}/columns` (list columns)
- `POST /api/metadata/{connection_id}/refresh` (refresh cache)

---

### Scenario 3: Execute SELECT Query (P1)

**Goal**: Verify users can write and execute SQL queries with results display.

**Steps**:
1. From connections list, click "Query" on a connection
2. **Expected**: See Monaco Editor with SQL syntax highlighting
3. Type a SELECT query: `SELECT * FROM users LIMIT 10`
4. Click "Run" or press Cmd/Ctrl+Enter
5. **Expected**: See results table with columns and 10 rows
6. **Expected**: See execution time (e.g., "145ms")
7. Try query without LIMIT: `SELECT * FROM users`
8. Click "Run"
9. **Expected**: See results with auto-applied LIMIT 1000
10. **Expected**: See message "LIMIT 1000 automatically applied"
11. Try non-SELECT query: `UPDATE users SET name = 'test'`
12. Click "Run"
13. **Expected**: See error "Only SELECT statements are allowed"
14. Try invalid SQL: `SELEC * FROM users` (typo)
15. Click "Run"
16. **Expected**: See syntax error with line number before execution

**Validation Checklist**:
- [ ] Monaco Editor provides syntax highlighting
- [ ] Autocomplete suggests table/column names
- [ ] SELECT queries execute successfully
- [ ] Results table displays all columns and rows
- [ ] LIMIT 1000 auto-applied when missing
- [ ] Non-SELECT queries rejected with clear error
- [ ] SQL syntax errors shown before execution
- [ ] Query saved to history (check query_history table)

**API Endpoints Used**:
- `POST /api/queries/validate` (validate SQL before execution)
- `POST /api/queries/execute` (execute query)
- `GET /api/queries/history/{connection_id}` (view history)

---

### Scenario 4: Natural Language to SQL (P3)

**Goal**: Verify users can generate SQL from natural language descriptions.

**Steps**:
1. On query page, click "NL2SQL" tab
2. Type natural language: "show all users created in the last 7 days"
3. Click "Generate SQL"
4. **Expected**: See loading indicator
5. **Expected**: See generated SQL (e.g., `SELECT * FROM users WHERE created_at > NOW() - INTERVAL '7 days'`)
6. **Expected**: See explanation of what query does
7. Review SQL in editor (auto-populated)
8. Make manual edits if needed
9. Click "Run" to execute
10. **Expected**: See results table

**Validation Checklist**:
- [ ] NL2SQL generates syntactically correct SQL
- [ ] Generated SQL uses actual table/column names from schema
- [ ] Explanation is clear and helpful
- [ ] Warnings shown for ambiguous inputs
- [ ] Generated SQL can be edited before execution
- [ ] Confidence level (high/medium/low) displayed

**API Endpoints Used**:
- `POST /api/nl2sql` (convert natural language to SQL)

**Note**: Requires OpenAI API key in environment variable `OPENAI_API_KEY`

---

### Scenario 5: Export Query Results (P2)

**Goal**: Verify users can export query results to CSV, JSON, and Excel.

**Steps**:
1. Execute a query with results (e.g., `SELECT * FROM users LIMIT 50`)
2. Click "Export" dropdown
3. Select "Export as CSV"
4. **Expected**: CSV file downloads with filename "query_results.csv"
5. Open CSV file
6. **Expected**: See all columns and 50 rows with proper formatting
7. Return to results table
8. Click "Export" → "Export as JSON"
9. **Expected**: JSON file downloads
10. Open JSON file
11. **Expected**: See array of objects with all rows
12. Return to results table
13. Click "Export" → "Export as Excel"
14. **Expected**: XLSX file downloads
15. Open Excel file
16. **Expected**: See formatted table with headers and data

**Validation Checklist**:
- [ ] CSV export includes all rows (not just current page)
- [ ] CSV handles special characters (quotes, commas, newlines)
- [ ] JSON export is valid JSON array
- [ ] Excel export has formatted headers
- [ ] NULL values displayed correctly in all formats
- [ ] Large result sets (1000 rows) export successfully

**API Endpoints Used**:
- `POST /api/exports/csv` (export as CSV)
- `POST /api/exports/json` (export as JSON)
- `POST /api/exports/excel` (export as Excel)

---

## Performance Validation

### Metadata Performance (Success Criteria: SC-002, SC-003)

```bash
# Run performance test for metadata fetch
python backend/tests/integration/test_metadata_performance.py

# Expected results:
# - First fetch (no cache): < 5 seconds for 100 tables
# - Cached fetch: < 1 second
```

### Query Execution Performance (Success Criteria: SC-004)

```bash
# Run performance test for query execution
python backend/tests/integration/test_query_performance.py

# Expected results:
# - Simple SELECT with < 1000 rows: < 3 seconds
# - Includes network, execution, and serialization time
```

### NL2SQL Performance (Success Criteria: SC-006)

```bash
# Run performance test for NL2SQL
python backend/tests/integration/test_nl2sql_performance.py

# Expected results:
# - NL2SQL conversion: < 10 seconds
# - Includes OpenAI API call time
```

---

## Security Validation

### SQL Injection Prevention

```bash
# Run security tests
python backend/tests/contract/test_sql_security.py

# Validates:
# - Only SELECT statements allowed
# - SQL injection attempts rejected
# - Malicious SQL patterns detected
```

**Manual Tests**:
1. Try SQL injection: `SELECT * FROM users WHERE id = 1; DROP TABLE users;`
   - **Expected**: Rejected by sqlglot parser
2. Try subquery with DELETE: `SELECT * FROM users WHERE id IN (DELETE FROM users)`
   - **Expected**: Rejected (not a SELECT-only query)

### Password Encryption

```bash
# Check SQLite database
sqlite3 ~/.db_query/db_query.db "SELECT id, name, password_encrypted FROM connections;"

# Expected:
# - password_encrypted column contains Fernet ciphertext
# - Ciphertext starts with "gAAAAA..." (base64-encoded)
# - No plain passwords visible
```

---

## Troubleshooting

### Backend Issues

**Problem**: FastAPI won't start
```bash
# Check Python version
python --version  # Should be 3.12+

# Check if port 8000 is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Check dependencies
pip list | grep fastapi
```

**Problem**: Database connection fails
```bash
# Test PostgreSQL connection manually
psql -h localhost -p 5432 -U postgres -d postgres

# Check PostgreSQL is running
ps aux | grep postgres  # macOS/Linux
```

**Problem**: Encryption key missing
```bash
# Regenerate encryption key
python -c "from cryptography.fernet import Fernet; import os; key = Fernet.generate_key(); os.makedirs(os.path.expanduser('~/.db_query'), exist_ok=True); open(os.path.expanduser('~/.db_query/secret.key'), 'wb').write(key)"
```

### Frontend Issues

**Problem**: Frontend won't start
```bash
# Check Node version
node --version  # Should be 18+

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check if port 5173 is in use
lsof -i :5173  # macOS/Linux
```

**Problem**: API calls fail (CORS)
```bash
# Check backend CORS configuration in src/main.py
# Ensure CORS allows http://localhost:5173
```

**Problem**: Monaco Editor not loading
```bash
# Check browser console for errors
# Verify @monaco-editor/react is installed
npm list @monaco-editor/react
```

---

## Success Metrics

After completing all scenarios:

- [ ] All P1 user stories (US1, US3) validated ✅ MVP Complete
- [ ] All P2 user stories (US2, US5) validated ✅ Enhanced Complete  
- [ ] All P3 user stories (US4) validated ✅ Full Feature Complete
- [ ] All performance criteria met (SC-002 to SC-007)
- [ ] All security validations passed
- [ ] Backend API documentation accessible and accurate
- [ ] Frontend UI responsive and intuitive

---

## Next Steps

Once quickstart validation is complete:

1. **Run automated tests**: `pytest backend/tests` and `npm test` in frontend
2. **Check code coverage**: Should be ≥80% for backend
3. **Review API documentation**: Verify OpenAPI schema matches implementation
4. **Performance profiling**: Identify bottlenecks for optimization
5. **User acceptance testing**: Get feedback from real users

---

## Support

For issues during quickstart validation:
- Check logs: `tail -f backend/logs/app.log`
- Review SQLite database: `sqlite3 ~/.db_query/db_query.db`
- API health check: `curl http://localhost:8000/health`
- Frontend console: Open browser DevTools → Console tab

---

**Quickstart Guide Complete** ✅

This guide validates the complete feature implementation across all user stories and success criteria. Use it to verify the system works end-to-end before deployment.
