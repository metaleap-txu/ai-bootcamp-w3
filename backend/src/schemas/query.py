"""Pydantic schemas for query execution and validation."""
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class ColumnMetadata(BaseModel):
    """Schema for column metadata in query results."""
    
    name: str
    type: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "id",
                "type": "integer",
            }
        }
    }


class QueryExecuteRequest(BaseModel):
    """Schema for executing a query."""
    
    connection_id: int = Field(..., description="ID of the connection to use")
    sql: str = Field(..., min_length=1, description="SQL query to execute")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "connection_id": 1,
                "sql": "SELECT * FROM users WHERE active = true",
            }
        }
    }


class QueryResult(BaseModel):
    """Schema for query execution results."""
    
    columns: List[ColumnMetadata]
    rows: List[List[Any]]
    row_count: int
    execution_time_ms: int
    transformed_sql: Optional[str] = Field(
        None, description="SQL after transformation (e.g., LIMIT injection)"
    )
    message: Optional[str] = Field(None, description="Info message (e.g., 'LIMIT 1000 applied')")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "columns": [
                    {"name": "id", "type": "integer"},
                    {"name": "name", "type": "varchar"},
                    {"name": "active", "type": "boolean"},
                ],
                "rows": [
                    [1, "Alice", True],
                    [2, "Bob", True],
                ],
                "row_count": 2,
                "execution_time_ms": 45,
                "transformed_sql": "SELECT * FROM users WHERE active = true LIMIT 1000",
                "message": "LIMIT 1000 automatically applied",
            }
        }
    }


class QueryValidateRequest(BaseModel):
    """Schema for validating SQL syntax."""
    
    sql: str = Field(..., min_length=1, description="SQL query to validate")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "sql": "SELECT * FROM users",
            }
        }
    }


class ValidationResult(BaseModel):
    """Schema for SQL validation results."""
    
    valid: bool
    error: Optional[str] = None
    transformed_sql: Optional[str] = Field(
        None, description="SQL after transformation (e.g., LIMIT injection)"
    )
    message: Optional[str] = Field(None, description="Info message")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "valid": True,
                    "transformed_sql": "SELECT * FROM users LIMIT 1000",
                    "message": "LIMIT 1000 automatically applied",
                },
                {
                    "valid": False,
                    "error": "Only SELECT statements are allowed",
                },
            ]
        }
    }


class QueryHistoryItem(BaseModel):
    """Schema for query history item."""
    
    id: int
    connection_id: int
    query_text: str
    executed_at: datetime
    execution_time_ms: int
    row_count: Optional[int]
    success: bool
    error_message: Optional[str]
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "connection_id": 1,
                "query_text": "SELECT * FROM users LIMIT 10",
                "executed_at": "2025-12-25T10:30:00",
                "execution_time_ms": 45,
                "row_count": 10,
                "success": True,
                "error_message": None,
            }
        }
    }
