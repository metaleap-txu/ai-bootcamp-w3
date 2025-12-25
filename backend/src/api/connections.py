"""API endpoints for database connection management."""
from typing import List
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.schemas.connection import (
    ConnectionCreate,
    ConnectionUpdate,
    ConnectionResponse,
    ConnectionTestRequest,
    ConnectionTestResponse,
)
from src.services.connection_service import ConnectionService
from src.utils.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


def get_connection_service(db: Session = Depends(get_db)) -> ConnectionService:
    """Dependency to get ConnectionService instance."""
    return ConnectionService(db)


@router.get("/", response_model=List[ConnectionResponse])
async def list_connections(
    service: ConnectionService = Depends(get_connection_service),
) -> List[ConnectionResponse]:
    """
    Get all database connections.
    
    Returns:
        List[ConnectionResponse]: List of all connections (without passwords)
    """
    connections = service.get_all()
    return [ConnectionResponse.model_validate(conn) for conn in connections]


@router.post("/", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(
    connection_data: ConnectionCreate,
    service: ConnectionService = Depends(get_connection_service),
) -> ConnectionResponse:
    """
    Create a new database connection.
    
    Args:
        connection_data: Connection creation data
        
    Returns:
        ConnectionResponse: Created connection (without password)
        
    Raises:
        HTTPException: If connection name already exists
    """
    try:
        connection = service.create(connection_data)
        return ConnectionResponse.model_validate(connection)
    except ValueError as e:
        logger.warning(f"Invalid connection data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except SQLAlchemyError as e:
        logger.error(f"Database error creating connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create connection due to database error",
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error creating connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        ) from e


@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(
    connection_id: int,
    service: ConnectionService = Depends(get_connection_service),
) -> ConnectionResponse:
    """
    Get a specific connection by ID.
    
    Args:
        connection_id: Connection ID
        
    Returns:
        ConnectionResponse: Connection details (without password)
        
    Raises:
        HTTPException: If connection not found
    """
    connection = service.get_by_id(connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection with ID {connection_id} not found",
        )
    return ConnectionResponse.model_validate(connection)


@router.put("/{connection_id}", response_model=ConnectionResponse)
async def update_connection(
    connection_id: int,
    update_data: ConnectionUpdate,
    service: ConnectionService = Depends(get_connection_service),
) -> ConnectionResponse:
    """
    Update an existing connection.
    
    Args:
        connection_id: Connection ID
        update_data: Connection update data
        
    Returns:
        ConnectionResponse: Updated connection (without password)
        
    Raises:
        HTTPException: If connection not found or update fails
    """
    try:
        connection = service.update(connection_id, update_data)
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connection with ID {connection_id} not found",
            )
        return ConnectionResponse.model_validate(connection)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    connection_id: int,
    service: ConnectionService = Depends(get_connection_service),
) -> None:
    """
    Delete a connection.
    
    Args:
        connection_id: Connection ID
        
    Raises:
        HTTPException: If connection not found
    """
    deleted = service.delete(connection_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection with ID {connection_id} not found",
        )


@router.post("/test", response_model=ConnectionTestResponse)
async def test_connection(
    test_request: ConnectionTestRequest,
    service: ConnectionService = Depends(get_connection_service),
) -> ConnectionTestResponse:
    """
    Test a database connection.
    
    Can test either an existing connection by ID or a new connection with provided credentials.
    
    Args:
        test_request: Test request with either connection_id or connection parameters
        
    Returns:
        ConnectionTestResponse: Test result
        
    Raises:
        HTTPException: If connection_id provided but not found
    """
    try:
        if test_request.connection_id is not None:
            # Test existing connection
            return await service.test_connection_by_id(test_request.connection_id)
        else:
            # Test ad-hoc connection
            return await service.test_connection(
                host=test_request.host,  # type: ignore
                port=test_request.port,  # type: ignore
                database=test_request.database,  # type: ignore
                username=test_request.username,  # type: ignore
                password=test_request.password,  # type: ignore
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
