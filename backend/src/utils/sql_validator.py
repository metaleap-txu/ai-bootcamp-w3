"""SQL validation utilities using sqlglot."""
from typing import Tuple

import sqlglot
from sqlglot import exp


class SQLValidationError(Exception):
    """Exception raised for SQL validation failures."""

    pass


def validate_and_transform_query(sql: str) -> Tuple[str, str]:
    """
    Validate SQL is SELECT-only and add LIMIT if missing.
    
    Args:
        sql: SQL query string to validate and transform
        
    Returns:
        Tuple[str, str]: (transformed_sql, message)
        - transformed_sql: SQL with LIMIT 1000 applied if needed
        - message: Information message about transformation (empty if no changes)
        
    Raises:
        SQLValidationError: If SQL is not a SELECT statement or has syntax errors
        
    Examples:
        >>> sql = "SELECT * FROM users"
        >>> transformed, msg = validate_and_transform_query(sql)
        >>> "LIMIT 1000" in transformed
        True
        >>> msg
        'LIMIT 1000 automatically applied'
        
        >>> sql = "SELECT * FROM users LIMIT 10"
        >>> transformed, msg = validate_and_transform_query(sql)
        >>> "LIMIT 10" in transformed
        True
        >>> msg
        ''
        
        >>> sql = "DELETE FROM users"
        >>> validate_and_transform_query(sql)
        Traceback (most recent call last):
        ...
        SQLValidationError: Only SELECT statements are allowed
    """
    try:
        # Parse SQL into AST
        parsed = sqlglot.parse_one(sql, dialect="postgres")
    except sqlglot.ParseError as e:
        raise SQLValidationError(f"SQL syntax error: {str(e)}") from e
    
    # Check if SELECT statement
    if not isinstance(parsed, exp.Select):
        raise SQLValidationError(
            "Only SELECT statements are allowed. "
            "INSERT, UPDATE, DELETE, DROP, and other statements are forbidden."
        )
    
    # Check if LIMIT already exists
    message = ""
    if not parsed.args.get("limit"):
        # Add LIMIT 1000
        parsed = parsed.limit(1000)
        message = "LIMIT 1000 automatically applied"
    
    # Convert back to SQL string
    transformed_sql = parsed.sql(dialect="postgres")
    
    return transformed_sql, message


def validate_sql_syntax(sql: str) -> Tuple[bool, str]:
    """
    Validate SQL syntax without executing.
    
    Args:
        sql: SQL query string to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
        - is_valid: True if syntax is valid
        - error_message: Empty string if valid, error description if invalid
        
    Examples:
        >>> validate_sql_syntax("SELECT * FROM users")
        (True, '')
        
        >>> is_valid, error = validate_sql_syntax("SELEC * FROM users")
        >>> is_valid
        False
        >>> "syntax error" in error.lower()
        True
    """
    try:
        sqlglot.parse_one(sql, dialect="postgres")
        return True, ""
    except sqlglot.ParseError as e:
        return False, f"SQL syntax error: {str(e)}"
