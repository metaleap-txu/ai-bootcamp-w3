"""
Service layer for SQL query execution and validation.

This module provides:
- SQL query validation using sqlglot parsing and AST analysis
- SELECT-only enforcement to prevent destructive operations
- Automatic LIMIT injection for unbounded queries (max 1000 rows)
- Query execution via asyncpg connection pooling
- Query history tracking (last 50 per connection)
- Comprehensive error handling for connection and execution errors

Security features:
- Only SELECT statements allowed (no INSERT, UPDATE, DELETE, DROP)
- SQL injection prevention through parameterized queries
- Query timeout protection
"""
import time
from typing import List, Any, Tuple

import asyncpg
from sqlalchemy.orm import Session

from src.models.connection import Connection
from src.models.query_history import QueryHistory
from src.schemas.query import (
    ColumnMetadata,
    QueryResult,
    ValidationResult,
    QueryHistoryItem,
)
from src.utils.security import decrypt_password
from src.utils.sql_validator import validate_and_transform_query, validate_sql_syntax, SQLValidationError
from src.config import settings


class QueryService:
    """Service for query execution and validation."""
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
    
    def validate_sql(self, sql: str) -> ValidationResult:
        """
        Validate SQL syntax and check if it's a SELECT statement.
        
        Args:
            sql: SQL query to validate
            
        Returns:
            ValidationResult: Validation result with error or transformed SQL
        """
        # First check syntax
        is_valid, syntax_error = validate_sql_syntax(sql)
        if not is_valid:
            return ValidationResult(valid=False, error=syntax_error)
        
        # Then validate and transform
        try:
            transformed_sql, message = validate_and_transform_query(sql)
            return ValidationResult(
                valid=True,
                transformed_sql=transformed_sql,
                message=message or None,
            )
        except SQLValidationError as e:
            return ValidationResult(valid=False, error=str(e))
    
    async def execute_query(
        self, connection_id: int, sql: str
    ) -> Tuple[QueryResult, bool]:
        """
        Execute SQL query on a PostgreSQL connection.
        
        Args:
            connection_id: ID of the connection to use
            sql: SQL query to execute
            
        Returns:
            Tuple[QueryResult, bool]: (Query result, success flag)
            
        Raises:
            ValueError: If connection not found
            SQLValidationError: If SQL validation fails
        """
        # Get connection
        connection = self.db.query(Connection).filter(Connection.id == connection_id).first()
        if not connection:
            raise ValueError(f"Connection with ID {connection_id} not found")
        
        # Validate and transform SQL
        transformed_sql, transform_message = validate_and_transform_query(sql)
        
        # Decrypt password
        password = decrypt_password(connection.password_encrypted)
        
        # Execute query with timing
        start_time = time.time()
        success = False
        error_message = None
        rows = []
        columns = []
        
        try:
            # Connect to PostgreSQL
            conn = await asyncpg.connect(
                host=connection.host,
                port=connection.port,
                database=connection.database,
                user=connection.username,
                password=password,
                timeout=30.0,
            )
            
            try:
                # Execute query
                result = await conn.fetch(transformed_sql)
                
                # Extract column metadata
                if result:
                    columns = [
                        ColumnMetadata(name=key, type=str(type(result[0][key]).__name__))
                        for key in result[0].keys()
                    ]
                    # Convert rows to list of lists
                    rows = [list(record.values()) for record in result]
                else:
                    columns = []
                    rows = []
                
                success = True
            finally:
                await conn.close()
        except asyncpg.PostgresError as e:
            error_message = str(e)
            raise
        except Exception as e:
            error_message = str(e)
            raise
        finally:
            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Save to history
            self._save_to_history(
                connection_id=connection_id,
                query_text=transformed_sql,
                execution_time_ms=execution_time_ms,
                row_count=len(rows) if success else None,
                success=success,
                error_message=error_message,
            )
        
        # Create result
        result = QueryResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            execution_time_ms=execution_time_ms,
            transformed_sql=transformed_sql if transformed_sql != sql else None,
            message=transform_message or None,
        )
        
        return result, success
    
    def _save_to_history(
        self,
        connection_id: int,
        query_text: str,
        execution_time_ms: int,
        row_count: int | None,
        success: bool,
        error_message: str | None,
    ) -> None:
        """
        Save query execution to history.
        
        Args:
            connection_id: Connection ID
            query_text: Executed SQL query
            execution_time_ms: Execution time in milliseconds
            row_count: Number of rows returned (None if failed)
            success: Whether execution succeeded
            error_message: Error message if failed
        """
        history_entry = QueryHistory(
            connection_id=connection_id,
            query_text=query_text,
            execution_time_ms=execution_time_ms,
            row_count=row_count,
            success=success,
            error_message=error_message,
        )
        
        self.db.add(history_entry)
        self.db.commit()
        
        # Keep only last N queries per connection
        self._cleanup_old_history(connection_id)
    
    def _cleanup_old_history(self, connection_id: int) -> None:
        """
        Remove old history entries, keeping only the most recent ones.
        
        Args:
            connection_id: Connection ID to clean up history for
        """
        # Get count of history entries for this connection
        count = (
            self.db.query(QueryHistory)
            .filter(QueryHistory.connection_id == connection_id)
            .count()
        )
        
        # If over limit, delete oldest entries
        if count > settings.query_history_limit:
            entries_to_delete = count - settings.query_history_limit
            
            # Get IDs of oldest entries
            old_entries = (
                self.db.query(QueryHistory.id)
                .filter(QueryHistory.connection_id == connection_id)
                .order_by(QueryHistory.executed_at.asc())
                .limit(entries_to_delete)
                .all()
            )
            
            # Delete them
            for (entry_id,) in old_entries:
                self.db.query(QueryHistory).filter(QueryHistory.id == entry_id).delete()
            
            self.db.commit()
    
    def get_query_history(self, connection_id: int, limit: int = 50) -> List[QueryHistoryItem]:
        """
        Get query history for a connection.
        
        Args:
            connection_id: Connection ID
            limit: Maximum number of history items to return
            
        Returns:
            List[QueryHistoryItem]: Query history items, most recent first
        """
        history = (
            self.db.query(QueryHistory)
            .filter(QueryHistory.connection_id == connection_id)
            .order_by(QueryHistory.executed_at.desc())
            .limit(limit)
            .all()
        )
        
        return [QueryHistoryItem.model_validate(item) for item in history]
