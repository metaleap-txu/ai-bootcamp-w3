"""JSON formatter service with custom encoding."""
import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Iterator


class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for database types.
    
    Handles:
    - datetime/date objects → ISO 8601 strings
    - Decimal → float
    - Other types → default JSONEncoder behavior
    """
    
    def default(self, obj: Any) -> Any:
        """
        Override default encoding for special types.
        
        Args:
            obj: Object to encode
        
        Returns:
            JSON-serializable representation
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        
        if isinstance(obj, date):
            return obj.isoformat()
        
        if isinstance(obj, Decimal):
            return float(obj)
        
        # Fall back to default behavior
        return super().default(obj)


class JSONFormatter:
    """
    JSON formatter with streaming support and custom encoding.
    
    Features:
    - Custom encoder for datetime/Decimal types
    - Pretty printing option
    - Chunk-based generation for large datasets
    - Valid JSON array format for streaming
    """
    
    def __init__(self, pretty: bool = False, indent: int = 2):
        """
        Initialize JSON formatter.
        
        Args:
            pretty: Enable pretty printing with indentation
            indent: Number of spaces for indentation (if pretty=True)
        """
        self.pretty = pretty
        self.indent = indent if pretty else None
    
    def format_rows(
        self,
        columns: list[str],
        rows: list[dict[str, Any]],
        chunk_size: int = 1000
    ) -> Iterator[str]:
        """
        Format data as JSON chunks for streaming.
        
        Generates valid JSON array format with chunked output:
        [
          {"col1": "val1", ...},
          {"col1": "val2", ...}
        ]
        
        Args:
            columns: List of column names (for filtering)
            rows: List of row dictionaries
            chunk_size: Number of rows per chunk
        
        Yields:
            JSON formatted strings (chunks)
        
        Example:
            >>> formatter = JSONFormatter(pretty=True)
            >>> columns = ["id", "name"]
            >>> rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
            >>> for chunk in formatter.format_rows(columns, rows):
            ...     print(chunk)
        """
        # Open JSON array
        if self.pretty:
            yield "[\n"
        else:
            yield "["
        
        total_rows = len(rows)
        row_index = 0
        
        # Process in chunks
        for i in range(0, total_rows, chunk_size):
            chunk = rows[i:i + chunk_size]
            
            for row in chunk:
                # Filter row to only include specified columns
                filtered_row = {col: row.get(col) for col in columns if col in row}
                
                # Encode row as JSON
                json_str = json.dumps(
                    filtered_row,
                    cls=CustomJSONEncoder,
                    ensure_ascii=False,
                    indent=self.indent
                )
                
                # Add indentation for pretty printing
                if self.pretty:
                    # Indent each line of the JSON object
                    indented_lines = [f"  {line}" for line in json_str.split('\n')]
                    json_str = '\n'.join(indented_lines)
                
                # Add comma separator except for last row
                if row_index < total_rows - 1:
                    json_str += ","
                
                # Add newline for pretty printing
                if self.pretty:
                    json_str += "\n"
                
                yield json_str
                row_index += 1
        
        # Close JSON array
        if self.pretty:
            yield "]\n"
        else:
            yield "]"
    
    def format_complete(
        self,
        columns: list[str],
        rows: list[dict[str, Any]]
    ) -> str:
        """
        Format entire dataset as single JSON string.
        
        Args:
            columns: List of column names
            rows: List of row dictionaries
        
        Returns:
            Complete JSON as string
        
        Note:
            For large datasets, use format_rows() for streaming instead
        """
        # Filter all rows
        filtered_rows = [
            {col: row.get(col) for col in columns if col in row}
            for row in rows
        ]
        
        # Encode as JSON
        return json.dumps(
            filtered_rows,
            cls=CustomJSONEncoder,
            ensure_ascii=False,
            indent=self.indent
        )
