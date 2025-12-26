"""Filename sanitization utility for secure export filenames."""
import re
from datetime import datetime


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    Sanitize a filename to prevent path traversal and ensure filesystem compatibility.
    
    Args:
        filename: Raw filename to sanitize
        max_length: Maximum length for the filename (default 200)
    
    Returns:
        Sanitized filename safe for filesystem use
    
    Examples:
        >>> sanitize_filename("my report")
        'my_report'
        >>> sanitize_filename("../../../etc/passwd")
        'etc_passwd'
        >>> sanitize_filename("user@data<2024>")
        'user_data_2024'
    """
    if not filename or not filename.strip():
        return "export"
    
    # Remove any path components (path traversal attack prevention)
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Remove or replace unsafe characters
    # Keep alphanumeric, dash, underscore, period
    filename = re.sub(r'[^\w\-.]', '_', filename)
    
    # Remove leading/trailing periods and underscores
    filename = filename.strip('._')
    
    # Collapse multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Truncate to max length
    if len(filename) > max_length:
        filename = filename[:max_length].rstrip('_.')
    
    # If sanitization resulted in empty string, use default
    if not filename:
        return "export"
    
    return filename


def generate_export_filename(
    prefix: str | None = None,
    format: str = "csv",
    timestamp: datetime | None = None
) -> str:
    """
    Generate a timestamped export filename.
    
    Args:
        prefix: Custom filename prefix (will be sanitized)
        format: File format extension ('csv' or 'json')
        timestamp: Custom timestamp (default: current time)
    
    Returns:
        Complete filename with sanitized prefix and timestamp
    
    Examples:
        >>> generate_export_filename("sales report", "csv")
        'sales_report_20251225_143022.csv'
        >>> generate_export_filename(None, "json")
        'query_results_20251225_143022.json'
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    # Sanitize prefix
    if prefix:
        sanitized_prefix = sanitize_filename(prefix)
    else:
        sanitized_prefix = "query_results"
    
    # Generate timestamp string
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    
    # Validate format
    if format not in ("csv", "json"):
        format = "csv"
    
    # Combine components
    filename = f"{sanitized_prefix}_{timestamp_str}.{format}"
    
    return filename
