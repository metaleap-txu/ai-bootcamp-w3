"""API endpoints for database metadata operations."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.schemas.metadata import (
    Schema,
    Table,
    TableDetails,
    MetadataRefreshResponse,
)
from src.services.metadata_service import MetadataService
from src.utils.database import get_db

router = APIRouter()


def get_metadata_service(db: Session = Depends(get_db)) -> MetadataService:
    """Dependency to get MetadataService instance."""
    return MetadataService(db)


@router.get("/{connection_id}/schemas", response_model=List[Schema])
async def list_schemas(
    connection_id: int,
    use_cache: bool = True,
    service: MetadataService = Depends(get_metadata_service),
) -> List[Schema]:
    """
    Get list of schemas for a connection.
    
    Args:
        connection_id: Connection ID
        use_cache: Whether to use cached data (default True)
        
    Returns:
        List[Schema]: List of schemas
        
    Raises:
        HTTPException: If connection not found or fetch fails
    """
    try:
        return await service.get_schemas(connection_id, use_cache=use_cache)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch schemas: {str(e)}",
        ) from e


@router.get("/{connection_id}/schemas/{schema_name}/tables", response_model=List[Table])
async def list_tables(
    connection_id: int,
    schema_name: str,
    use_cache: bool = True,
    service: MetadataService = Depends(get_metadata_service),
) -> List[Table]:
    """
    Get list of tables for a schema.
    
    Args:
        connection_id: Connection ID
        schema_name: Schema name
        use_cache: Whether to use cached data (default True)
        
    Returns:
        List[Table]: List of tables
        
    Raises:
        HTTPException: If connection not found or fetch fails
    """
    try:
        return await service.get_tables(connection_id, schema_name, use_cache=use_cache)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tables: {str(e)}",
        ) from e


@router.get(
    "/{connection_id}/schemas/{schema_name}/tables/{table_name}",
    response_model=TableDetails,
)
async def get_table_details(
    connection_id: int,
    schema_name: str,
    table_name: str,
    use_cache: bool = True,
    service: MetadataService = Depends(get_metadata_service),
) -> TableDetails:
    """
    Get detailed information about a table.
    
    Args:
        connection_id: Connection ID
        schema_name: Schema name
        table_name: Table name
        use_cache: Whether to use cached data (default True)
        
    Returns:
        TableDetails: Table details with columns and foreign keys
        
    Raises:
        HTTPException: If connection not found or fetch fails
    """
    try:
        return await service.get_table_details(
            connection_id, schema_name, table_name, use_cache=use_cache
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch table details: {str(e)}",
        ) from e


@router.post("/{connection_id}/refresh", response_model=MetadataRefreshResponse)
async def refresh_metadata(
    connection_id: int,
    service: MetadataService = Depends(get_metadata_service),
) -> MetadataRefreshResponse:
    """
    Clear cached metadata for a connection.
    
    Args:
        connection_id: Connection ID
        
    Returns:
        MetadataRefreshResponse: Refresh result
    """
    try:
        service.refresh_metadata(connection_id)
        return MetadataRefreshResponse(
            success=True,
            message="Metadata cache cleared successfully",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh metadata: {str(e)}",
        ) from e
