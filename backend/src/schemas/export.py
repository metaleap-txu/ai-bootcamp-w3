"""Pydantic schemas for query result exports."""
from typing import List, Any

from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    """Schema for export request."""
    
    columns: List[str] = Field(..., description="Column names")
    rows: List[List[Any]] = Field(..., description="Row data")
    filename: str = Field(
        ...,
        description="Base filename (without extension)",
        min_length=1,
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "columns": ["id", "name", "email"],
                "rows": [
                    [1, "Alice", "alice@example.com"],
                    [2, "Bob", "bob@example.com"],
                ],
                "filename": "users_export",
            }
        }
    }
