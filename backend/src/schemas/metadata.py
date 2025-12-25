"""Pydantic schemas for database metadata."""
from typing import List, Optional

from pydantic import BaseModel, Field


class Column(BaseModel):
    """Schema for a database column."""
    
    name: str
    data_type: str
    is_nullable: bool
    column_default: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "id",
                "data_type": "integer",
                "is_nullable": False,
                "column_default": "nextval('users_id_seq'::regclass)",
            }
        }
    }


class ForeignKey(BaseModel):
    """Schema for a foreign key constraint."""
    
    column_name: str
    referenced_table: str
    referenced_column: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "column_name": "user_id",
                "referenced_table": "users",
                "referenced_column": "id",
            }
        }
    }


class TableDetails(BaseModel):
    """Schema for detailed table information."""
    
    name: str
    schema: str
    row_count: Optional[int] = None
    columns: List[Column]
    foreign_keys: List[ForeignKey] = Field(default_factory=list)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "users",
                "schema": "public",
                "row_count": 1523,
                "columns": [
                    {
                        "name": "id",
                        "data_type": "integer",
                        "is_nullable": False,
                        "column_default": "nextval('users_id_seq'::regclass)",
                    },
                    {
                        "name": "username",
                        "data_type": "character varying",
                        "is_nullable": False,
                        "column_default": None,
                    },
                ],
                "foreign_keys": [],
            }
        }
    }


class Table(BaseModel):
    """Schema for a database table."""
    
    name: str
    schema: str
    table_type: str  # 'BASE TABLE', 'VIEW', etc.
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "users",
                "schema": "public",
                "table_type": "BASE TABLE",
            }
        }
    }


class Schema(BaseModel):
    """Schema for a database schema."""
    
    name: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "public",
            }
        }
    }


class MetadataRefreshResponse(BaseModel):
    """Schema for metadata refresh response."""
    
    success: bool
    message: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Metadata cache refreshed successfully",
            }
        }
    }
