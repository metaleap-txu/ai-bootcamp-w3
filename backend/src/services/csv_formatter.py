"""CSV formatter service with RFC 4180 compliance."""
import csv
import io
from typing import Any, Iterator


class CSVFormatter:
    """
    RFC 4180 compliant CSV formatter with streaming support.
    
    Features:
    - Proper quote escaping (double quotes for embedded quotes)
    - CRLF line endings
    - UTF-8 encoding with optional BOM
    - Chunk-based generation for memory efficiency
    """
    
    def __init__(self, include_bom: bool = True):
        """
        Initialize CSV formatter.
        
        Args:
            include_bom: Whether to include UTF-8 BOM at start of file
        """
        self.include_bom = include_bom
    
    def format_rows(
        self,
        columns: list[str],
        rows: list[dict[str, Any]],
        chunk_size: int = 1000
    ) -> Iterator[str]:
        """
        Format data as CSV chunks for streaming.
        
        Args:
            columns: List of column names (CSV header)
            rows: List of row dictionaries
            chunk_size: Number of rows per chunk
        
        Yields:
            CSV formatted strings (chunks)
        
        Example:
            >>> formatter = CSVFormatter()
            >>> columns = ["id", "name"]
            >>> rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
            >>> for chunk in formatter.format_rows(columns, rows):
            ...     print(chunk)
        """
        # Yield UTF-8 BOM if requested
        if self.include_bom:
            yield '\ufeff'
        
        # Process in chunks
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i + chunk_size]
            
            # Use StringIO buffer for this chunk
            buffer = io.StringIO()
            writer = csv.DictWriter(
                buffer,
                fieldnames=columns,
                lineterminator='\r\n',  # RFC 4180 CRLF
                quoting=csv.QUOTE_MINIMAL,
                quotechar='"',
                escapechar=None  # Use double-quote escaping
            )
            
            # Write header only for first chunk
            if i == 0:
                writer.writeheader()
            
            # Write rows
            for row in chunk:
                # Filter row to only include columns in header order
                filtered_row = {col: self._format_value(row.get(col)) for col in columns}
                writer.writerow(filtered_row)
            
            # Get chunk content and yield
            chunk_content = buffer.getvalue()
            buffer.close()
            
            if chunk_content:
                yield chunk_content
    
    def _format_value(self, value: Any) -> str:
        """
        Format a single cell value for CSV output.
        
        Args:
            value: Raw cell value
        
        Returns:
            String representation suitable for CSV
        """
        if value is None:
            return ""
        
        # Convert to string
        return str(value)
    
    def format_complete(
        self,
        columns: list[str],
        rows: list[dict[str, Any]]
    ) -> str:
        """
        Format entire dataset as single CSV string.
        
        Args:
            columns: List of column names
            rows: List of row dictionaries
        
        Returns:
            Complete CSV as string
        
        Note:
            For large datasets, use format_rows() for streaming instead
        """
        chunks = list(self.format_rows(columns, rows, chunk_size=len(rows) or 1))
        return ''.join(chunks)
