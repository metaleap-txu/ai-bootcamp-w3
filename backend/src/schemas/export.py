"""Pydantic schemas for export operations."""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


# Export Request Schemas

class QueryResultData(BaseModel):
    """In-memory query result data for export."""
    
    columns: list[str] = Field(..., description="Column names")
    rows: list[dict] = Field(..., description="Row data as list of dictionaries")
    total_rows: int = Field(..., description="Total number of rows")
    
    @field_validator('columns')
    @classmethod
    def validate_columns(cls, v: list[str]) -> list[str]:
        """Validate columns list is not empty."""
        if not v:
            raise ValueError("columns cannot be empty")
        return v
    
    @field_validator('rows')
    @classmethod
    def validate_rows(cls, v: list[dict]) -> list[dict]:
        """Validate rows list."""
        # Rows can be empty (valid for zero-result queries)
        return v


class ExportOptions(BaseModel):
    """Format-specific export options."""
    
    pretty: bool = Field(False, description="Pretty-print JSON with indentation (JSON only)")
    include_bom: bool = Field(False, description="Include UTF-8 BOM for Excel (CSV only)")
    include_metadata: bool = Field(False, description="Include query metadata in export")


class ExportRequest(BaseModel):
    """Request payload for export operations."""
    
    query_history_id: Optional[int] = Field(None, description="ID of query history to export")
    query_result: Optional[QueryResultData] = Field(None, description="In-memory query result")
    format: Literal["csv", "json"] = Field(..., description="Export file format")
    options: ExportOptions = Field(default_factory=ExportOptions, description="Export options")
    filename: Optional[str] = Field(None, max_length=200, description="Custom filename prefix")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query_history_id": 42,
                    "format": "csv",
                    "options": {"include_bom": True}
                },
                {
                    "query_result": {
                        "columns": ["id", "email"],
                        "rows": [{"id": 1, "email": "test@example.com"}]
                    },
                    "format": "json",
                    "options": {"pretty": True, "include_metadata": True}
                }
            ]
        }
    }


# Export Response Schemas

class ExportResponseStreaming(BaseModel):
    """Response for streaming export operations."""
    
    status: Literal["streaming"] = Field("streaming", description="Export status")
    stream_url: str = Field(..., description="SSE URL for progress updates")
    export_id: str = Field(..., description="Unique export operation identifier")
    filename: str = Field(..., description="Generated filename")
    row_count: int = Field(..., ge=0, description="Total rows to export")
    format: Literal["csv", "json"] = Field(..., description="Export format")


# Export Preferences Schemas

class ExportPreferencesCreate(BaseModel):
    """Schema for creating export preferences."""
    
    user_id: int = Field(..., ge=1, description="User identifier")
    default_format: Literal["csv", "json"] = Field("csv", description="Default export format")
    include_metadata: bool = Field(False, description="Include metadata by default")
    pretty_json: bool = Field(False, description="Pretty-print JSON by default")
    csv_include_bom: bool = Field(False, description="Include UTF-8 BOM in CSV by default")


class ExportPreferencesUpdate(BaseModel):
    """Schema for updating export preferences."""
    
    default_format: Optional[Literal["csv", "json"]] = Field(None, description="Default format")
    include_metadata: Optional[bool] = Field(None, description="Include metadata by default")
    pretty_json: Optional[bool] = Field(None, description="Pretty-print JSON")
    csv_include_bom: Optional[bool] = Field(None, description="Include UTF-8 BOM in CSV")


class ExportPreferencesResponse(BaseModel):
    """Schema for export preferences response."""
    
    user_id: int
    default_format: str
    include_metadata: bool
    pretty_json: bool
    csv_include_bom: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# Export History Schemas

class ExportHistoryCreate(BaseModel):
    """Schema for creating export history entry."""
    
    user_id: Optional[int] = None
    query_history_id: Optional[int] = None
    format: Literal["csv", "json"]
    row_count: int = Field(..., ge=0)
    file_size_bytes: Optional[int] = Field(None, ge=0)
    status: Literal["success", "failed", "cancelled"]
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = Field(None, ge=0)
    filename: str = Field(..., max_length=255)


class ExportHistoryResponse(BaseModel):
    """Schema for export history response."""
    
    id: int
    user_id: Optional[int]
    query_history_id: Optional[int]
    format: str
    row_count: int
    file_size_bytes: Optional[int]
    status: str
    error_message: Optional[str]
    execution_time_ms: Optional[int]
    exported_at: datetime
    filename: str
    
    model_config = {"from_attributes": True}


class ExportHistoryListResponse(BaseModel):
    """Schema for export history list response."""
    
    exports: list[ExportHistoryResponse]
    total: int


# Error Response Schema

class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: str = Field(..., description="Human-readable error message")
    code: Optional[str] = Field(None, description="Machine-readable error code")
    details: Optional[dict] = Field(None, description="Additional error details")
