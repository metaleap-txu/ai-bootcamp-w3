"""Streaming export service for large datasets."""
from typing import Any, Iterator
import logging

from ..schemas.export import QueryResultData, ExportOptions
from .csv_formatter import CSVFormatter
from .json_formatter import JSONFormatter


logger = logging.getLogger(__name__)

# Configuration for streaming
STREAM_CHUNK_SIZE = 1000  # Rows per chunk
LARGE_DATASET_THRESHOLD = 10000  # Rows


class StreamExporter:
    """
    Handles streaming exports for large datasets with memory efficiency.
    
    Features:
    - Chunk-based processing to prevent memory overflow
    - Progress tracking for long-running exports
    - Graceful error handling with partial data recovery
    - Support for CSV and JSON formats
    """
    
    def __init__(self, chunk_size: int = STREAM_CHUNK_SIZE):
        """
        Initialize stream exporter.
        
        Args:
            chunk_size: Number of rows to process per chunk
        """
        self.chunk_size = chunk_size
        self.csv_formatter = CSVFormatter()
        self.json_formatter = JSONFormatter()
    
    def is_large_dataset(self, row_count: int) -> bool:
        """
        Determine if dataset should use streaming approach.
        
        Args:
            row_count: Total number of rows
        
        Returns:
            True if streaming should be used
        """
        return row_count > LARGE_DATASET_THRESHOLD
    
    def stream_csv(
        self,
        data: QueryResultData,
        options: ExportOptions | None = None,
    ) -> Iterator[str]:
        """
        Stream CSV export for large datasets.
        
        Args:
            data: Query result data
            options: Export options
        
        Yields:
            CSV formatted chunks
        
        Example:
            >>> exporter = StreamExporter()
            >>> data = QueryResultData(columns=["id", "name"], rows=[...], total_rows=50000)
            >>> for chunk in exporter.stream_csv(data):
            ...     # chunk is sent to client immediately
            ...     pass
        """
        try:
            logger.info(
                f"Starting CSV streaming export: {data.total_rows} rows, "
                f"chunk_size={self.chunk_size}"
            )
            
            rows_processed = 0
            
            # Stream chunks
            for chunk in self.csv_formatter.format_rows(
                data.columns,
                data.rows,
                chunk_size=self.chunk_size
            ):
                yield chunk
                
                # Estimate progress (rough)
                chunk_size_estimate = chunk.count('\n')
                rows_processed += chunk_size_estimate
                
                if rows_processed % 5000 == 0:
                    logger.info(f"CSV export progress: {rows_processed} rows processed")
            
            logger.info(f"CSV streaming export completed: {data.total_rows} rows")
        
        except Exception as e:
            logger.error(f"CSV streaming export failed: {e}")
            # Yield error marker or allow exception to propagate
            raise
    
    def stream_json(
        self,
        data: QueryResultData,
        options: ExportOptions | None = None,
    ) -> Iterator[str]:
        """
        Stream JSON export for large datasets.
        
        Args:
            data: Query result data
            options: Export options
        
        Yields:
            JSON formatted chunks
        
        Example:
            >>> exporter = StreamExporter()
            >>> data = QueryResultData(columns=["id", "name"], rows=[...], total_rows=50000)
            >>> for chunk in exporter.stream_json(data):
            ...     # chunk is sent to client immediately
            ...     pass
        """
        try:
            logger.info(
                f"Starting JSON streaming export: {data.total_rows} rows, "
                f"chunk_size={self.chunk_size}"
            )
            
            # Use pretty print option if specified
            pretty = options.pretty if options else False
            json_formatter = JSONFormatter(pretty=pretty)
            
            rows_processed = 0
            
            # Stream chunks
            for chunk in json_formatter.format_rows(
                data.columns,
                data.rows,
                chunk_size=self.chunk_size
            ):
                yield chunk
                
                # Track progress
                rows_processed += self.chunk_size
                
                if rows_processed % 5000 == 0 and rows_processed <= data.total_rows:
                    logger.info(f"JSON export progress: {rows_processed}/{data.total_rows} rows")
            
            logger.info(f"JSON streaming export completed: {data.total_rows} rows")
        
        except Exception as e:
            logger.error(f"JSON streaming export failed: {e}")
            raise
    
    def estimate_size_bytes(
        self,
        data: QueryResultData,
        format: str = "csv"
    ) -> int:
        """
        Estimate export file size in bytes.
        
        Args:
            data: Query result data
            format: Export format ('csv' or 'json')
        
        Returns:
            Estimated file size in bytes
        
        Note:
            This is a rough estimate for progress tracking
        """
        # Sample-based estimation
        if len(data.rows) == 0:
            return 0
        
        # Take first 10 rows as sample
        sample_size = min(10, len(data.rows))
        sample_rows = data.rows[:sample_size]
        
        if format == "csv":
            # Estimate CSV size
            formatter = CSVFormatter()
            sample_chunks = list(formatter.format_rows(data.columns, sample_rows))
            sample_bytes = sum(len(chunk.encode('utf-8')) for chunk in sample_chunks)
            
            # Extrapolate to full dataset
            avg_bytes_per_row = sample_bytes / sample_size
            estimated_total = int(avg_bytes_per_row * data.total_rows)
        else:
            # Estimate JSON size
            formatter = JSONFormatter()
            sample_chunks = list(formatter.format_rows(data.columns, sample_rows))
            sample_bytes = sum(len(chunk.encode('utf-8')) for chunk in sample_chunks)
            
            # Extrapolate to full dataset
            avg_bytes_per_row = sample_bytes / sample_size
            estimated_total = int(avg_bytes_per_row * data.total_rows)
        
        return estimated_total
