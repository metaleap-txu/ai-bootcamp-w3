"""Base Pydantic schemas for common response models."""
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "ValidationError",
                "message": "Only SELECT statements are allowed",
                "details": {"sql": "DELETE FROM users"},
            }
        }
    }


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str
    version: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
            }
        }
    }
