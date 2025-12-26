# Quickstart Guide: Data Export Module

**Feature**: Data Export Module  
**Phase**: 1 (Design & Contracts)  
**Date**: December 25, 2025

## Overview

This guide provides quick examples for implementing and using the data export functionality. It covers API usage, integration patterns, and common workflows.

---

## Quick Start: Export Query Results

### 1. Basic CSV Export (Direct Download)

Export small query results (<10K rows) as CSV:

```bash
curl -X POST http://localhost:8000/api/exports/csv \
  -H "Content-Type: application/json" \
  -d '{
    "query_history_id": 42,
    "format": "csv"
  }' \
  --output query_results.csv
```

**Response**: CSV file download with headers:
```
Content-Disposition: attachment; filename="query_results_20251225_143022.csv"
Content-Type: text/csv; charset=utf-8
```

---

### 2. JSON Export with Options

Export query results as pretty-printed JSON with metadata:

```bash
curl -X POST http://localhost:8000/api/exports/json \
  -H "Content-Type: application/json" \
  -d '{
    "query_history_id": 42,
    "format": "json",
    "options": {
      "pretty": true,
      "include_metadata": true
    }
  }' \
  --output query_results.json
```

**Response**: JSON file download:
```json
{
  "metadata": {
    "query": "SELECT * FROM users WHERE active = true",
    "executed_at": "2025-12-25T14:30:22",
    "row_count": 150
  },
  "results": [
    {"id": 1, "email": "alice@example.com", "created_at": "2025-12-01T10:30:00"},
    {"id": 2, "email": "bob@example.com", "created_at": "2025-12-02T14:15:00"}
  ]
}
```

---

### 3. Large Export with Streaming

For large datasets (>10K rows), the API returns a streaming URL:

```bash
curl -X POST http://localhost:8000/api/exports/csv \
  -H "Content-Type: application/json" \
  -d '{
    "query_history_id": 99,
    "format": "csv"
  }'
```

**Response** (HTTP 202):
```json
{
  "status": "streaming",
  "stream_url": "/api/exports/stream/abc123def456",
  "export_id": "abc123def456",
  "filename": "large_export_20251225_143022.csv",
  "row_count": 150000,
  "format": "csv"
}
```

**Connect to SSE stream**:
```bash
curl -N http://localhost:8000/api/exports/stream/abc123def456
```

**SSE events**:
```
data: {"progress": 25.5, "processed": 25500, "total": 100000, "status": "in_progress"}

data: {"progress": 50.0, "processed": 50000, "total": 100000, "status": "in_progress"}

data: {"progress": 100.0, "processed": 100000, "total": 100000, "status": "complete", "download_url": "/api/exports/download/abc123"}
```

**Download completed file**:
```bash
curl http://localhost:8000/api/exports/download/abc123 --output large_export.csv
```

---

## Frontend Integration Examples

### 1. React Component: Export Button

```tsx
import { Button, message } from 'antd';
import { exportService } from '../services/exportService';

const ExportButton: React.FC<{ queryHistoryId: number }> = ({ queryHistoryId }) => {
  const [loading, setLoading] = useState(false);

  const handleExport = async (format: 'csv' | 'json') => {
    setLoading(true);
    try {
      const response = await exportService.exportQueryResult({
        query_history_id: queryHistoryId,
        format,
      });

      if (response.status === 'success') {
        // Direct download
        window.location.href = response.download_url;
        message.success(`Export successful: ${response.filename}`);
      } else if (response.status === 'streaming') {
        // Handle streaming export
        handleStreamingExport(response.stream_url, response.filename);
      }
    } catch (error) {
      message.error('Export failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button.Group>
      <Button onClick={() => handleExport('csv')} loading={loading}>
        Export CSV
      </Button>
      <Button onClick={() => handleExport('json')} loading={loading}>
        Export JSON
      </Button>
    </Button.Group>
  );
};
```

---

### 2. Streaming Export with Progress Indicator

```tsx
import { Progress, Modal } from 'antd';
import { useEffect, useState } from 'react';

const StreamingExportModal: React.FC<{ streamUrl: string; filename: string }> = ({
  streamUrl,
  filename,
}) => {
  const [progress, setProgress] = useState(0);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  useEffect(() => {
    const eventSource = new EventSource(streamUrl);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.status === 'in_progress') {
        setProgress(data.progress);
      } else if (data.status === 'complete') {
        setProgress(100);
        setDownloadUrl(data.download_url);
        eventSource.close();
      }
    };

    eventSource.onerror = () => {
      message.error('Streaming export failed');
      eventSource.close();
    };

    return () => eventSource.close();
  }, [streamUrl]);

  return (
    <Modal
      open={true}
      title="Exporting Data"
      footer={
        downloadUrl ? (
          <Button type="primary" href={downloadUrl} download>
            Download {filename}
          </Button>
        ) : null
      }
    >
      <Progress percent={Math.round(progress)} status={downloadUrl ? 'success' : 'active'} />
      <p>{downloadUrl ? 'Export complete!' : 'Generating export file...'}</p>
    </Modal>
  );
};
```

---

## Backend Implementation Examples

### 1. CSV Export Service

```python
import csv
import io
from typing import List, Dict

class CSVExportService:
    def generate_csv(
        self,
        columns: List[str],
        rows: List[Dict],
        include_bom: bool = False
    ) -> str:
        """Generate RFC 4180 compliant CSV."""
        output = io.StringIO()
        
        # Add UTF-8 BOM for Excel compatibility
        if include_bom:
            output.write('\ufeff')
        
        writer = csv.DictWriter(
            output,
            fieldnames=columns,
            quoting=csv.QUOTE_MINIMAL,
            lineterminator='\r\n'
        )
        
        writer.writeheader()
        writer.writerows(rows)
        
        return output.getvalue()

    def stream_csv(
        self,
        query_cursor,
        columns: List[str],
        batch_size: int = 1000
    ):
        """Stream CSV in chunks for large datasets."""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns, quoting=csv.QUOTE_MINIMAL)
        
        # Yield header
        writer.writeheader()
        yield output.getvalue().encode('utf-8')
        output.truncate(0)
        output.seek(0)
        
        # Yield data in batches
        batch = []
        async for row in query_cursor:
            batch.append(dict(zip(columns, row)))
            
            if len(batch) >= batch_size:
                writer.writerows(batch)
                yield output.getvalue().encode('utf-8')
                output.truncate(0)
                output.seek(0)
                batch = []
        
        # Yield remaining rows
        if batch:
            writer.writerows(batch)
            yield output.getvalue().encode('utf-8')
```

---

### 2. FastAPI Export Endpoint

```python
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel

router = APIRouter(prefix="/api/exports", tags=["exports"])

class ExportRequest(BaseModel):
    query_history_id: int | None = None
    query_result: dict | None = None
    format: Literal["csv", "json"]
    options: dict = {}

@router.post("/csv")
async def export_csv(request: ExportRequest):
    # Validate request
    if not request.query_history_id and not request.query_result:
        raise HTTPException(400, "Must provide query_history_id or query_result")
    
    # Fetch query result
    if request.query_history_id:
        query_result = await query_service.get_query_result(request.query_history_id)
    else:
        query_result = request.query_result
    
    # Determine export strategy
    row_count = len(query_result['rows'])
    
    if row_count < 10000:
        # Small export: direct download
        csv_content = csv_service.generate_csv(
            columns=query_result['columns'],
            rows=query_result['rows'],
            include_bom=request.options.get('include_bom', False)
        )
        
        filename = generate_filename("query_results", "csv")
        
        return Response(
            content=csv_content.encode('utf-8'),
            media_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
    else:
        # Large export: streaming
        export_id = generate_export_id()
        filename = generate_filename("large_export", "csv")
        
        # Store export task for streaming
        await export_queue.enqueue(export_id, query_result, request.format)
        
        return {
            "status": "streaming",
            "stream_url": f"/api/exports/stream/{export_id}",
            "export_id": export_id,
            "filename": filename,
            "row_count": row_count,
            "format": "csv"
        }
```

---

## Common Workflows

### Workflow 1: Manual Export After Query

1. User executes query → receives query_history_id
2. User clicks "Export" button → selects format (CSV/JSON)
3. Frontend calls `/api/exports/{format}` with query_history_id
4. Backend returns file or streaming URL
5. File downloads to user's browser

### Workflow 2: One-Click "Run & Export"

1. User has saved query with export preferences
2. User clicks "Run & Export" button
3. Frontend executes query AND export in sequence
4. Export uses user's default format preference
5. File downloads automatically after query completes

### Workflow 3: Natural Language Export

1. User executes query → sees results
2. User types: "export this as spreadsheet"
3. AI interprets intent → format = CSV
4. AI confirms: "I'll export this as CSV for spreadsheet use"
5. AI triggers `/api/exports/csv` with current query_history_id
6. File downloads

### Workflow 4: Batch Export

1. User selects multiple queries from history
2. User clicks "Export All as ZIP"
3. Frontend calls batch export endpoint (future enhancement)
4. Backend generates individual exports, packages in ZIP
5. ZIP file downloads

---

## User Preference Management

### Get User Preferences

```bash
curl http://localhost:8000/api/export-preferences
```

**Response**:
```json
{
  "user_id": 1,
  "default_format": "csv",
  "include_metadata": false,
  "pretty_json": false,
  "csv_include_bom": false,
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T14:30:00Z"
}
```

### Update User Preferences

```bash
curl -X PUT http://localhost:8000/api/export-preferences \
  -H "Content-Type: application/json" \
  -d '{
    "default_format": "json",
    "pretty_json": true,
    "include_metadata": true
  }'
```

---

## Export History

### View Recent Exports

```bash
curl http://localhost:8000/api/export-history?limit=10
```

**Response**:
```json
{
  "exports": [
    {
      "id": 123,
      "query_history_id": 42,
      "format": "csv",
      "row_count": 1500,
      "file_size_bytes": 153600,
      "status": "success",
      "execution_time_ms": 2340,
      "exported_at": "2025-12-25T14:30:22Z",
      "filename": "query_results_20251225_143022.csv"
    }
  ],
  "total": 45
}
```

---

## Testing Examples

### Contract Test: CSV Export Endpoint

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_csv_export_success(client: AsyncClient):
    response = await client.post(
        "/api/exports/csv",
        json={
            "query_history_id": 1,
            "format": "csv"
        }
    )
    
    assert response.status_code == 200
    assert response.headers['content-type'] == 'text/csv; charset=utf-8'
    assert 'attachment' in response.headers['content-disposition']
    assert '.csv' in response.headers['content-disposition']
    
    # Verify CSV content
    csv_content = response.text
    assert 'id,email,created_at' in csv_content  # Header row
    assert len(csv_content.split('\n')) > 1  # Has data rows

@pytest.mark.asyncio
async def test_csv_export_invalid_request(client: AsyncClient):
    response = await client.post(
        "/api/exports/csv",
        json={
            "format": "csv"
            # Missing both query_history_id and query_result
        }
    )
    
    assert response.status_code == 400
    assert 'error' in response.json()
```

---

## Next Steps

1. **Implement Backend Services**: CSV formatter, JSON serializer, streaming logic
2. **Create API Endpoints**: Export routes, preference management, history
3. **Build Frontend Components**: Export buttons, progress indicators, preference UI
4. **Write Tests**: Contract tests for API, integration tests for formatters
5. **Add AI Integration**: Natural language export command interpretation

See [tasks.md](tasks.md) for detailed implementation breakdown (generated by `/speckit.tasks` command).

---

## Quickstart Complete

All API contracts, integration patterns, and common workflows documented. Ready for implementation phase.
