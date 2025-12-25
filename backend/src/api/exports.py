"""API endpoints for exporting query results."""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from src.schemas.export import ExportRequest
from src.services.export_service import ExportService

router = APIRouter()


@router.post("/csv")
async def export_csv(request: ExportRequest) -> Response:
    """
    Export query results to CSV format.
    
    Args:
        request: Export request with columns, rows, and filename
        
    Returns:
        Response: CSV file content with proper headers
        
    Raises:
        HTTPException: If export fails
    """
    try:
        csv_content = ExportService.export_to_csv(request.columns, request.rows)
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{request.filename}.csv"'
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export to CSV: {str(e)}",
        ) from e


@router.post("/json")
async def export_json(request: ExportRequest) -> Response:
    """
    Export query results to JSON format.
    
    Args:
        request: Export request with columns, rows, and filename
        
    Returns:
        Response: JSON file content with proper headers
        
    Raises:
        HTTPException: If export fails
    """
    try:
        json_content = ExportService.export_to_json(request.columns, request.rows)
        
        return Response(
            content=json_content,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="{request.filename}.json"'
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export to JSON: {str(e)}",
        ) from e


@router.post("/excel")
async def export_excel(request: ExportRequest) -> Response:
    """
    Export query results to Excel format.
    
    Args:
        request: Export request with columns, rows, and filename
        
    Returns:
        Response: Excel file content with proper headers
        
    Raises:
        HTTPException: If export fails
    """
    try:
        excel_content = ExportService.export_to_excel(request.columns, request.rows)
        
        return Response(
            content=excel_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{request.filename}.xlsx"'
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export to Excel: {str(e)}",
        ) from e
