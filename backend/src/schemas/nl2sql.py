"""Pydantic schemas for Natural Language to SQL conversion."""
from typing import Optional

from pydantic import BaseModel, Field


class NL2SQLRequest(BaseModel):
    """Schema for NL2SQL generation request."""
    
    connection_id: int = Field(..., description="Connection ID for schema context")
    natural_language: str = Field(
        ...,
        min_length=1,
        description="Natural language description of the query",
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "connection_id": 1,
                "natural_language": "Show me all active users who registered in the last 30 days",
            }
        }
    }


class NL2SQLResponse(BaseModel):
    """Schema for NL2SQL generation response."""
    
    sql: str = Field(..., description="Generated SQL query")
    explanation: str = Field(..., description="Explanation of the generated SQL")
    confidence: str = Field(
        ...,
        description="Confidence level: 'high', 'medium', or 'low'",
    )
    warnings: Optional[str] = Field(
        None,
        description="Optional warnings about the generated SQL",
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "sql": "SELECT * FROM users WHERE active = true AND created_at >= CURRENT_DATE - INTERVAL '30 days'",
                "explanation": "This query selects all columns from the users table where the user is active and was created within the last 30 days.",
                "confidence": "high",
                "warnings": None,
            }
        }
    }
