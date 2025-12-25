# Research: Database Query Tool

**Feature**: Database Query Tool  
**Phase**: 0 (Research & Technology Validation)  
**Date**: 2025-12-25

## Overview

This document captures research findings for key technology decisions, best practices, and implementation patterns for the database query tool. All NEEDS CLARIFICATION items from the Technical Context have been resolved.

---

## Research Areas

### 1. SQL Validation with sqlglot

**Decision**: Use sqlglot for parsing, validation, and AST manipulation

**Rationale**:
- **Parse-only mode**: Can parse SQL without executing, perfect for pre-flight validation
- **AST inspection**: Can traverse AST to verify only SELECT statements allowed
- **Multi-dialect support**: Supports PostgreSQL, MySQL, SQLite, and others
- **LIMIT injection**: Can programmatically add LIMIT clause to AST before stringifying
- **Syntax error reporting**: Provides line/column error locations for user feedback
- **No database required**: Pure Python parsing, no DB connection needed for validation

**Alternatives considered**:
- **sqlparse**: Read-only parser, cannot modify AST to inject LIMIT clauses
- **regex-based validation**: Fragile, vulnerable to SQL injection, can't handle complex queries
- **pg_query**: PostgreSQL-specific, C extension dependencies, harder to deploy

**Implementation approach**:
```python
import sqlglot

def validate_and_transform_query(sql: str) -> tuple[bool, str, str]:
    """
    Validates SQL is SELECT-only and adds LIMIT if missing.
    Returns: (is_valid, transformed_sql, error_message)
    """
    try:
        # Parse SQL into AST
        parsed = sqlglot.parse_one(sql, dialect="postgres")
        
        # Check if SELECT statement
        if not isinstance(parsed, sqlglot.exp.Select):
            return False, "", "Only SELECT statements are allowed"
        
        # Check if LIMIT exists
        if not parsed.args.get("limit"):
            # Add LIMIT 1000
            parsed = parsed.limit(1000)
        
        # Convert back to SQL string
        transformed = parsed.sql(dialect="postgres")
        return True, transformed, ""
        
    except sqlglot.ParseError as e:
        return False, "", f"SQL syntax error: {str(e)}"
```

**References**: 
- https://github.com/tobymao/sqlglot
- sqlglot documentation on AST manipulation

---

### 2. PostgreSQL Async Driver Selection

**Decision**: Use asyncpg for PostgreSQL connections

**Rationale**:
- **Performance**: Fastest PostgreSQL driver for Python (C extension, asyncio-native)
- **Connection pooling**: Built-in async connection pool management
- **Type safety**: Returns native Python types, no manual conversion needed
- **FastAPI compatible**: Works seamlessly with async FastAPI endpoints
- **Metadata introspection**: Can query pg_catalog for schema/table/column metadata
- **Prepared statements**: Automatic prepared statement caching for repeated queries

**Alternatives considered**:
- **psycopg3**: Good alternative, but asyncpg benchmarks ~30% faster for read-heavy workloads
- **SQLAlchemy async**: Adds ORM overhead for dynamic query execution; better suited for static models
- **Databases library**: Simpler API but less control over connection lifecycle and pooling

**Implementation approach**:
```python
import asyncpg

async def execute_query(connection_string: str, sql: str):
    """Execute validated SQL query and return results."""
    pool = await asyncpg.create_pool(connection_string, min_size=1, max_size=5)
    
    async with pool.acquire() as conn:
        # Execute query
        rows = await conn.fetch(sql)
        
        # Get column metadata
        columns = [{"name": col.name, "type": str(col.python_type)} 
                   for col in rows[0].__class__.__fields__] if rows else []
        
        # Convert to dictionaries
        data = [dict(row) for row in rows]
        
    await pool.close()
    return {"columns": columns, "data": data, "row_count": len(data)}
```

**References**:
- https://github.com/MagicStack/asyncpg
- asyncpg performance benchmarks

---

### 3. Metadata Caching Strategy

**Decision**: Use SQLite with TTL-based cache invalidation

**Rationale**:
- **Persistent cache**: Survives application restarts, faster cold starts
- **Structured storage**: Store schema, tables, columns with relationships
- **TTL support**: Add `cached_at` timestamp, invalidate after 1 hour
- **Manual refresh**: Allow users to force refresh via API endpoint
- **No external dependencies**: SQLite bundled with Python, no Redis/Memcached needed
- **ACID guarantees**: Concurrent access handled safely

**Alternatives considered**:
- **In-memory dict**: Lost on restart, no persistence, no TTL management
- **Redis**: Overkill for local tool, adds deployment complexity
- **File-based JSON**: Slower for complex queries, no concurrent access safety

**Schema design**:
```python
class MetadataCache(Base):
    __tablename__ = "metadata_cache"
    
    id = Column(Integer, primary_key=True)
    connection_id = Column(Integer, ForeignKey("connections.id"))
    cache_type = Column(String)  # 'schemas', 'tables', 'columns'
    cache_data = Column(JSON)     # Nested JSON structure
    cached_at = Column(DateTime, default=datetime.utcnow)
    
    @property
    def is_expired(self) -> bool:
        """Check if cache is older than 1 hour."""
        return datetime.utcnow() - self.cached_at > timedelta(hours=1)
```

**References**:
- SQLAlchemy JSON column type documentation
- FastAPI caching patterns

---

### 4. Natural Language to SQL (NL2SQL) with OpenAI

**Decision**: Use OpenAI GPT-4 with schema context injection

**Rationale**:
- **Schema awareness**: Inject table/column names from metadata cache into prompt
- **Few-shot learning**: Include example queries in system prompt for better accuracy
- **Token efficiency**: Send only relevant schema (selected connection) to reduce costs
- **Streaming support**: Can stream partial SQL as it's generated
- **Validation**: Still validate generated SQL with sqlglot before execution

**Alternatives considered**:
- **Local models (Llama, Mistral)**: Lower accuracy, requires GPU, deployment complexity
- **Claude**: Comparable quality but OpenAI SDK more mature for streaming
- **Fine-tuned models**: Requires training data, maintenance overhead

**Prompt engineering approach**:
```python
async def nl_to_sql(natural_language: str, schema_context: dict) -> str:
    """Convert natural language to SQL using OpenAI."""
    
    # Build schema context
    schema_text = "\n".join([
        f"Table: {table['name']}\nColumns: {', '.join(table['columns'])}"
        for table in schema_context["tables"]
    ])
    
    system_prompt = f"""You are a PostgreSQL SQL expert. Generate SELECT queries only.
    
Available schema:
{schema_text}

Rules:
- Only SELECT statements
- Use proper table/column names from schema
- Add WHERE clauses for filters
- Include ORDER BY for sorting requests
- Return only the SQL query, no explanations
"""
    
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": natural_language}
        ],
        temperature=0.1  # Low temperature for deterministic output
    )
    
    return response.choices[0].message.content
```

**References**:
- OpenAI API documentation
- NL2SQL benchmarks (Spider, WikiSQL datasets)

---

### 5. Monaco Editor Integration

**Decision**: Use @monaco-editor/react with SQL language support

**Rationale**:
- **React integration**: Official React wrapper, well-maintained
- **SQL syntax highlighting**: Built-in SQL language support
- **Autocomplete**: Can provide custom autocomplete suggestions (table/column names)
- **Error markers**: Can show validation errors inline with line numbers
- **Keybindings**: Supports custom keybindings (e.g., Cmd+Enter to execute)
- **Themes**: Supports VS Code themes (dark/light mode)

**Alternatives considered**:
- **CodeMirror**: Lighter weight but less feature-rich, no native autocomplete
- **Ace Editor**: Older, less active maintenance
- **Plain textarea**: No syntax highlighting, poor UX for multi-line queries

**Implementation approach**:
```tsx
import Editor from '@monaco-editor/react';

function SqlEditor({ onExecute, schema }) {
  const handleEditorDidMount = (editor, monaco) => {
    // Register autocomplete provider
    monaco.languages.registerCompletionItemProvider('sql', {
      provideCompletionItems: (model, position) => {
        // Suggest table and column names from schema
        const suggestions = schema.tables.map(table => ({
          label: table.name,
          kind: monaco.languages.CompletionItemKind.Class,
          insertText: table.name,
        }));
        return { suggestions };
      }
    });
    
    // Cmd+Enter to execute
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      onExecute(editor.getValue());
    });
  };
  
  return (
    <Editor
      height="400px"
      language="sql"
      theme="vs-dark"
      onMount={handleEditorDidMount}
    />
  );
}
```

**References**:
- https://github.com/suren-atoyan/monaco-react
- Monaco Editor API documentation

---

### 6. Export Formats Implementation

**Decision**: Use pandas for CSV/Excel, native JSON for JSON export

**Rationale**:
- **pandas**: Industry standard for data manipulation, excellent Excel support via openpyxl
- **CSV**: pandas.to_csv() handles edge cases (quotes, newlines, null values)
- **Excel**: pandas.to_excel() creates formatted XLSX with proper types
- **JSON**: Standard library json.dumps() sufficient, no pandas overhead
- **Streaming**: Can stream large result sets to avoid memory issues

**Alternatives considered**:
- **csv module**: Manual handling of edge cases, no Excel support
- **xlsxwriter**: Lower-level, more complex API
- **DictWriter**: No type preservation, manual formatting

**Implementation approach**:
```python
import pandas as pd
from io import BytesIO

def export_to_csv(data: list[dict]) -> bytes:
    """Export query results to CSV."""
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode('utf-8')

def export_to_excel(data: list[dict]) -> bytes:
    """Export query results to Excel."""
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    return buffer.read()

def export_to_json(data: list[dict]) -> bytes:
    """Export query results to JSON."""
    return json.dumps(data, indent=2, default=str).encode('utf-8')
```

**References**:
- pandas documentation
- openpyxl for Excel generation

---

### 7. Password Security for Connection Storage

**Decision**: Use cryptography (Fernet) for symmetric encryption

**Rationale**:
- **Symmetric encryption**: Same key encrypts/decrypts passwords
- **Fernet**: High-level recipe from cryptography library, secure by default
- **Key management**: Store key in environment variable or secure file
- **Reversible**: Need to decrypt passwords to establish connections
- **PBKDF2**: Fernet uses PBKDF2 for key derivation

**Alternatives considered**:
- **bcrypt/argon2**: One-way hashing, can't decrypt for connections
- **AES manually**: Lower-level, easier to make mistakes
- **Plaintext**: Unacceptable security risk

**Implementation approach**:
```python
from cryptography.fernet import Fernet
import os

# Generate and store key (one-time setup)
# key = Fernet.generate_key()
# with open('~/.db_query/secret.key', 'wb') as f:
#     f.write(key)

def get_cipher():
    """Load encryption key and create cipher."""
    key_path = os.path.expanduser('~/.db_query/secret.key')
    with open(key_path, 'rb') as f:
        key = f.read()
    return Fernet(key)

def encrypt_password(password: str) -> str:
    """Encrypt password for storage."""
    cipher = get_cipher()
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(encrypted: str) -> str:
    """Decrypt password for connection."""
    cipher = get_cipher()
    return cipher.decrypt(encrypted.encode()).decode()
```

**References**:
- https://cryptography.io/en/latest/fernet/
- OWASP password storage guidelines

---

### 8. Frontend State Management

**Decision**: Use Refine's built-in data provider pattern

**Rationale**:
- **Refine integration**: dataProvider handles CRUD operations declaratively
- **Caching**: Automatic query caching via React Query under the hood
- **Optimistic updates**: Built-in support for optimistic UI updates
- **Error handling**: Standardized error handling across all API calls
- **No additional libraries**: No need for Redux/Zustand/Recoil

**Alternatives considered**:
- **Redux Toolkit**: Overkill for this application, adds boilerplate
- **Zustand**: Simpler but Refine's pattern already sufficient
- **Plain React Query**: Refine wraps it, provides higher-level abstractions

**Implementation approach**:
```tsx
import { Refine } from "@refinedev/core";
import dataProvider from "@refinedev/simple-rest";

function App() {
  return (
    <Refine
      dataProvider={dataProvider("http://localhost:8000/api")}
      resources={[
        { name: "connections", list: ConnectionsPage },
        { name: "queries", list: QueryPage },
      ]}
    />
  );
}
```

**References**:
- Refine data provider documentation
- React Query caching strategies

---

## Summary of Key Decisions

| Area | Technology | Key Benefit |
|------|------------|-------------|
| SQL Validation | sqlglot | AST manipulation for LIMIT injection |
| PostgreSQL Driver | asyncpg | Best async performance |
| Metadata Cache | SQLite with TTL | Persistent, structured, concurrent-safe |
| NL2SQL | OpenAI GPT-4 | Best accuracy with schema context |
| SQL Editor | Monaco Editor | VS Code-like experience |
| Export | pandas + native JSON | Industry standard, handles edge cases |
| Password Security | Fernet | Secure symmetric encryption |
| Frontend State | Refine dataProvider | Built-in caching and error handling |

All research complete. Ready to proceed to Phase 1: Design & Contracts.
