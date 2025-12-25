"""Pydantic schemas for database connections."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ConnectionCreate(BaseModel):
    """Schema for creating a new connection."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Unique connection name")
    host: str = Field(..., min_length=1, max_length=255, description="Database host")
    port: int = Field(..., ge=1, le=65535, description="Database port")
    database: str = Field(..., min_length=1, max_length=255, description="Database name")
    username: str = Field(..., min_length=1, max_length=255, description="Database username")
    password: str = Field(..., min_length=1, description="Database password (will be encrypted)")
    description: Optional[str] = Field(None, description="Optional connection description")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Production DB",
                "host": "localhost",
                "port": 5432,
                "database": "myapp",
                "username": "postgres",
                "password": "secret123",
                "description": "Production PostgreSQL database",
            }
        }
    }


class ConnectionUpdate(BaseModel):
    """Schema for updating an existing connection."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    host: Optional[str] = Field(None, min_length=1, max_length=255)
    port: Optional[int] = Field(None, ge=1, le=65535)
    database: Optional[str] = Field(None, min_length=1, max_length=255)
    username: Optional[str] = Field(None, min_length=1, max_length=255)
    password: Optional[str] = Field(None, min_length=1, description="New password (will be encrypted)")
    description: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Production DB Updated",
                "description": "Updated description",
            }
        }
    }


class ConnectionResponse(BaseModel):
    """Schema for connection response (without password)."""
    
    id: int
    name: str
    host: str
    port: int
    database: str
    username: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Production DB",
                "host": "localhost",
                "port": 5432,
                "database": "myapp",
                "username": "postgres",
                "description": "Production PostgreSQL database",
                "created_at": "2025-12-25T10:00:00",
                "updated_at": "2025-12-25T10:00:00",
            }
        }
    }


class ConnectionTestRequest(BaseModel):
    """Schema for testing a connection."""
    
    connection_id: Optional[int] = Field(None, description="ID of existing connection to test")
    host: Optional[str] = Field(None, description="Host for ad-hoc test")
    port: Optional[int] = Field(None, ge=1, le=65535)
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    
    @field_validator("connection_id")
    @classmethod
    def validate_connection_or_params(cls, v: Optional[int], info) -> Optional[int]:
        """Ensure either connection_id or connection params are provided."""
        if v is None:
            # If no connection_id, require all connection params
            data = info.data
            if not all([data.get("host"), data.get("port"), data.get("database"), 
                       data.get("username"), data.get("password")]):
                raise ValueError(
                    "Either connection_id or all connection parameters "
                    "(host, port, database, username, password) must be provided"
                )
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "connection_id": 1
                },
                {
                    "host": "localhost",
                    "port": 5432,
                    "database": "testdb",
                    "username": "postgres",
                    "password": "secret123"
                }
            ]
        }
    }


class ConnectionTestResponse(BaseModel):
    """Schema for connection test response."""
    
    success: bool
    message: str
    error: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "Connection successful"
                },
                {
                    "success": False,
                    "message": "Connection failed",
                    "error": "could not connect to server: Connection refused"
                }
            ]
        }
    }
