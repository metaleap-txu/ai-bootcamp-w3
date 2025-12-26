"""Export API endpoints for CSV and JSON data export."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..schemas.export import (
    ExportRequest,
    ExportResponseStreaming,
    ExportPreferencesCreate,
    ExportPreferencesUpdate,
    ExportPreferencesResponse,
    ExportHistoryResponse,
    ExportHistoryListResponse,
    ErrorResponse,
)
from ..services.export_service import ExportService
from ..utils.database import get_db
from ..utils.filename_sanitizer import generate_export_filename


router = APIRouter(prefix="/api/exports", tags=["exports"])


def get_export_service(db: Session = Depends(get_db)) -> ExportService:
    """Dependency to get export service instance."""
    return ExportService(db)


@router.post(
    "/csv",
    response_class=StreamingResponse,
    responses={
        200: {"description": "CSV file download"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Export failed"},
    },
)
async def export_csv(
    request: ExportRequest,
    service: ExportService = Depends(get_export_service),
):
    """
    Export query results as CSV file.
    
    Supports both direct download (small datasets) and streaming (large datasets).
    """
    try:
        # Validate request has data
        if not request.query_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data to export. Provide query_result or query_history_id.",
            )
        
        # Check if data is empty
        if request.query_result.total_rows == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data to export. Query returned 0 rows.",
            )
        
        # Generate filename
        filename = generate_export_filename(
            prefix=request.filename,
            format="csv",
        )
        
        # Log export history (before streaming starts)
        try:
            # Estimate file size for history
            estimated_size = service.stream_exporter.estimate_size_bytes(
                request.query_result, format="csv"
            )
            
            service.create_export_history(
                user_id="default_user",  # TODO: Get from auth context
                format="csv",
                filename=filename,
                row_count=request.query_result.total_rows,
                query_history_id=request.query_history_id,
                file_size_bytes=estimated_size,
                status="completed",
            )
        except Exception as log_error:
            # Don't fail export if history logging fails
            print(f"Failed to log export history: {log_error}")
        
        # Export CSV
        csv_chunks = service.export_csv(request.query_result, request.options)
        
        # Create streaming response
        response = StreamingResponse(
            csv_chunks,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        # Log failed export
        try:
            service.create_export_history(
                user_id="default_user",
                format="csv",
                filename="export_failed.csv",
                row_count=0,
                status="failed",
                error_message=str(e),
            )
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}",
        )


@router.post(
    "/json",
    response_class=StreamingResponse,
    responses={
        200: {"description": "JSON file download"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Export failed"},
    },
)
async def export_json(
    request: ExportRequest,
    service: ExportService = Depends(get_export_service),
):
    """
    Export query results as JSON file.
    
    Supports both direct download (small datasets) and streaming (large datasets).
    """
    try:
        # Validate request has data
        if not request.query_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data to export. Provide query_result or query_history_id.",
            )
        
        # Check if data is empty
        if request.query_result.total_rows == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data to export. Query returned 0 rows.",
            )
        
        # Generate filename
        filename = generate_export_filename(
            prefix=request.filename,
            format="json",
        )
        
        # Log export history (before streaming starts)
        try:
            # Estimate file size for history
            estimated_size = service.stream_exporter.estimate_size_bytes(
                request.query_result, format="json"
            )
            
            service.create_export_history(
                user_id="default_user",  # TODO: Get from auth context
                format="json",
                filename=filename,
                row_count=request.query_result.total_rows,
                query_history_id=request.query_history_id,
                file_size_bytes=estimated_size,
                status="completed",
            )
        except Exception as log_error:
            # Don't fail export if history logging fails
            print(f"Failed to log export history: {log_error}")
        
        # Export JSON
        json_chunks = service.export_json(request.query_result, request.options)
        
        # Create streaming response
        response = StreamingResponse(
            json_chunks,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        # Log failed export
        try:
            service.create_export_history(
                user_id="default_user",
                format="json",
                filename="export_failed.json",
                row_count=0,
                status="failed",
                error_message=str(e),
            )
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}",
        )


@router.get(
    "/history",
    response_model=ExportHistoryListResponse,
    responses={
        200: {"description": "Export history retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Failed to retrieve history"},
    },
)
async def get_export_history(
    user_id: str = "default_user",  # TODO: Get from auth context
    limit: int = 50,
    offset: int = 0,
    service: ExportService = Depends(get_export_service),
):
    """
    Retrieve export history for a user.
    
    Returns paginated list of export operations with metadata.
    """
    try:
        items, total = service.get_export_history(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        
        # Calculate pagination
        page = (offset // limit) + 1 if limit > 0 else 1
        
        return ExportHistoryListResponse(
            items=[
                ExportHistoryResponse(
                    id=item.id,
                    user_id=item.user_id,
                    query_history_id=item.query_history_id,
                    format=item.format,
                    filename=item.filename,
                    row_count=item.row_count,
                    file_size_bytes=item.file_size_bytes,
                    exported_at=item.exported_at.isoformat(),
                    status=item.status,
                    error_message=item.error_message,
                )
                for item in items
            ],
            total=total,
            page=page,
            page_size=limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve export history: {str(e)}",
        )
