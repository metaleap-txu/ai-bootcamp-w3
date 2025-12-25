"""API endpoints for Natural Language to SQL conversion."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.schemas.nl2sql import NL2SQLRequest, NL2SQLResponse
from src.services.nl2sql_service import NL2SQLService
from src.utils.database import get_db

router = APIRouter()


def get_nl2sql_service(db: Session = Depends(get_db)) -> NL2SQLService:
    """Dependency to get NL2SQLService instance."""
    return NL2SQLService(db)


@router.post("/generate", response_model=NL2SQLResponse)
async def generate_sql(
    request: NL2SQLRequest,
    service: NL2SQLService = Depends(get_nl2sql_service),
) -> NL2SQLResponse:
    """
    Generate SQL query from natural language description.
    
    Args:
        request: NL2SQL request with connection_id and natural_language
        
    Returns:
        NL2SQLResponse: Generated SQL with explanation and confidence
        
    Raises:
        HTTPException: If generation fails or OpenAI key not configured
    """
    try:
        return await service.generate_sql(
            connection_id=request.connection_id,
            natural_language=request.natural_language,
        )
    except ValueError as e:
        error_message = str(e)
        if "OpenAI API key" in error_message:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=error_message,
            ) from e
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message,
            ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SQL: {str(e)}",
        ) from e
