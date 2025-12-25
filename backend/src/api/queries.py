"""API endpoints for query execution and validation."""
from typing import List
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.schemas.query import (
    QueryExecuteRequest,
    QueryResult,
    QueryValidateRequest,
    ValidationResult,
    QueryHistoryItem,
)
from src.services.query_service import QueryService
from src.utils.database import get_db
from src.utils.sql_validator import SQLValidationError

logger = logging.getLogger(__name__)

router = APIRouter()


def get_query_service(db: Session = Depends(get_db)) -> QueryService:
    """Dependency to get QueryService instance."""
    return QueryService(db)


@router.post("/execute", response_model=QueryResult)
async def execute_query(
    request: QueryExecuteRequest,
    service: QueryService = Depends(get_query_service),
) -> QueryResult:
    """
    Execute a SQL query on a PostgreSQL database.
    
    Args:
        request: Query execution request with connection_id and SQL
        
    Returns:
        QueryResult: Query results with columns, rows, and metadata
        
    Raises:
        HTTPException: If connection not found, SQL invalid, or execution fails
    """
    try:
        result, success = await service.execute_query(
            connection_id=request.connection_id,
            sql=request.sql,
        )
        
        if not success:
            logger.error("Query execution failed without exception")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query execution failed",
            )
        
        return result
    except ValueError as e:
        logger.warning(f"Invalid query request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except SQLValidationError as e:
        logger.warning(f"SQL validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except ConnectionError as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to database: {str(e)}",
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error executing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}",
        ) from e


@router.post("/validate", response_model=ValidationResult)
async def validate_query(
    request: QueryValidateRequest,
    service: QueryService = Depends(get_query_service),
) -> ValidationResult:
    """
    Validate SQL syntax and check if it's a SELECT statement.
    
    Args:
        request: Validation request with SQL
        
    Returns:
        ValidationResult: Validation result with error or transformed SQL
    """
    return service.validate_sql(request.sql)


@router.get("/history/{connection_id}", response_model=List[QueryHistoryItem])
async def get_query_history(
    connection_id: int,
    limit: int = 50,
    service: QueryService = Depends(get_query_service),
) -> List[QueryHistoryItem]:
    """
    Get query history for a connection.
    
    Args:
        connection_id: Connection ID
        limit: Maximum number of history items to return (default 50)
        
    Returns:
        List[QueryHistoryItem]: Query history items, most recent first
    """
    return service.get_query_history(connection_id, limit)
