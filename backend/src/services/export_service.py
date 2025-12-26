"""Base export service for orchestrating export operations."""
from datetime import datetime
from typing import Any, Iterator

from sqlalchemy.orm import Session

from ..models.export_history import ExportHistory
from ..schemas.export import ExportHistoryCreate, ExportOptions, QueryResultData
from .csv_formatter import CSVFormatter
from .json_formatter import JSONFormatter
from .stream_exporter import StreamExporter


# Threshold for determining small vs streaming exports (in rows)
STREAMING_THRESHOLD = 10000


class ExportService:
    """
    Orchestrates export operations with format delegation and history tracking.
    
    Responsibilities:
    - Route exports to appropriate formatter (CSV/JSON)
    - Determine export strategy (small/streaming based on row count)
    - Log export history with metadata
    - Handle errors and status tracking
    """
    
    def __init__(self, db: Session):
        """
        Initialize export service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.csv_formatter = CSVFormatter()
        self.json_formatter = JSONFormatter()
        self.stream_exporter = StreamExporter()
    
    def should_stream(self, row_count: int) -> bool:
        """
        Determine if export should use streaming based on row count.
        
        Args:
            row_count: Number of rows to export
        
        Returns:
            True if streaming should be used, False for direct response
        """
        return row_count > STREAMING_THRESHOLD
    
    def export_csv(
        self,
        data: QueryResultData,
        options: ExportOptions | None = None
    ) -> Iterator[str]:
        """
        Export data as CSV format.
        
        Uses streaming for large datasets (>10K rows) for memory efficiency.
        
        Args:
            data: Query result data with columns and rows
            options: Export customization options
        
        Yields:
            CSV formatted chunks
        """
        options = options or ExportOptions()
        
        # Use stream exporter for large datasets
        if self.stream_exporter.is_large_dataset(data.total_rows):
            yield from self.stream_exporter.stream_csv(data, options)
        else:
            # Use regular formatter for small datasets
            csv_formatter = CSVFormatter(include_bom=True)
            yield from csv_formatter.format_rows(data.columns, data.rows)
    
    def export_json(
        self,
        data: QueryResultData,
        options: ExportOptions | None = None
    ) -> Iterator[str]:
        """
        Export data as JSON format.
        
        Uses streaming for large datasets (>10K rows) for memory efficiency.
        
        Args:
            data: Query result data with columns and rows
            options: Export customization options
        
        Yields:
            JSON formatted chunks
        """
        options = options or ExportOptions()
        
        # Use stream exporter for large datasets
        if self.stream_exporter.is_large_dataset(data.total_rows):
            yield from self.stream_exporter.stream_json(data, options)
        else:
            # Use regular formatter for small datasets
            json_formatter = JSONFormatter(pretty=options.pretty if options else False)
            yield from json_formatter.format_rows(data.columns, data.rows)
    
    def create_export_history(
        self,
        user_id: str,
        format: str,
        filename: str,
        row_count: int,
        query_history_id: int | None = None,
        file_size_bytes: int | None = None,
        status: str = "completed",
        error_message: str | None = None
    ) -> ExportHistory:
        """
        Create export history record.
        
        Args:
            user_id: User performing the export
            format: Export format ('csv' or 'json')
            filename: Generated filename
            row_count: Number of rows exported
            query_history_id: Optional reference to query history
            file_size_bytes: Optional file size in bytes
            status: Export status (default 'completed')
            error_message: Optional error message if failed
        
        Returns:
            Created ExportHistory instance
        """
        history_entry = ExportHistory(
            user_id=user_id,
            query_history_id=query_history_id,
            format=format,
            filename=filename,
            row_count=row_count,
            file_size_bytes=file_size_bytes,
            exported_at=datetime.utcnow(),
            status=status,
            error_message=error_message
        )
        
        self.db.add(history_entry)
        self.db.commit()
        self.db.refresh(history_entry)
        
        return history_entry
    
    def get_export_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[ExportHistory], int]:
        """
        Retrieve export history for a user.
        
        Args:
            user_id: User ID to filter by
            limit: Maximum number of records to return
            offset: Number of records to skip
        
        Returns:
            Tuple of (history entries, total count)
        """
        query = self.db.query(ExportHistory).filter(
            ExportHistory.user_id == user_id
        ).order_by(ExportHistory.exported_at.desc())
        
        total = query.count()
        items = query.limit(limit).offset(offset).all()
        
        return items, total
