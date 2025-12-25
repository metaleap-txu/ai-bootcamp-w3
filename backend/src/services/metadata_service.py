"""
Service layer for database metadata extraction and caching.

This module provides:
- Schema discovery from information_schema.schemata
- Table listing with type detection (BASE TABLE vs VIEW)
- Column metadata with data types, nullability, defaults
- Foreign key relationship detection via table_constraints
- Row count estimation using pg_class.reltuples (O(1) operation)
- Metadata caching with configurable TTL (default: 1 hour)

Caching strategy:
- Hierarchical: schemas → tables → table details
- TTL-based expiration (expires_at timestamp)
- Manual cache invalidation via refresh endpoint
- JSON serialization for flexible metadata storage
"""
import json
from datetime import datetime, timedelta
from typing import List, Optional

import asyncpg
from sqlalchemy.orm import Session

from src.models.connection import Connection
from src.models.metadata_cache import MetadataCache
from src.schemas.metadata import Schema, Table, Column, TableDetails, ForeignKey
from src.utils.security import decrypt_password
from src.config import settings


class MetadataService:
    """Service for fetching and caching database metadata."""
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
    
    async def get_schemas(self, connection_id: int, use_cache: bool = True) -> List[Schema]:
        """
        Get list of schemas for a connection.
        
        Args:
            connection_id: Connection ID
            use_cache: Whether to use cached data if available
            
        Returns:
            List[Schema]: List of schemas
            
        Raises:
            ValueError: If connection not found
        """
        # Check cache first
        if use_cache:
            cached = self._get_from_cache(
                connection_id=connection_id,
                metadata_type="schemas",
                schema_name="*",
            )
            if cached:
                return [Schema(**item) for item in json.loads(cached.metadata_json)]
        
        # Fetch from database
        connection = self._get_connection(connection_id)
        password = decrypt_password(connection.password_encrypted)
        
        conn = await asyncpg.connect(
            host=connection.host,
            port=connection.port,
            database=connection.database,
            user=connection.username,
            password=password,
        )
        
        try:
            # Query to get schemas
            query = """
                SELECT schema_name 
                FROM information_schema.schemata
                WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                ORDER BY schema_name
            """
            rows = await conn.fetch(query)
            schemas = [Schema(name=row["schema_name"]) for row in rows]
            
            # Cache the results
            self._save_to_cache(
                connection_id=connection_id,
                metadata_type="schemas",
                schema_name="*",
                table_name=None,
                data=schemas,
            )
            
            return schemas
        finally:
            await conn.close()
    
    async def get_tables(
        self, connection_id: int, schema_name: str, use_cache: bool = True
    ) -> List[Table]:
        """
        Get list of tables for a schema.
        
        Args:
            connection_id: Connection ID
            schema_name: Schema name
            use_cache: Whether to use cached data if available
            
        Returns:
            List[Table]: List of tables
            
        Raises:
            ValueError: If connection not found
        """
        # Check cache first
        if use_cache:
            cached = self._get_from_cache(
                connection_id=connection_id,
                metadata_type="tables",
                schema_name=schema_name,
            )
            if cached:
                return [Table(**item) for item in json.loads(cached.metadata_json)]
        
        # Fetch from database
        connection = self._get_connection(connection_id)
        password = decrypt_password(connection.password_encrypted)
        
        conn = await asyncpg.connect(
            host=connection.host,
            port=connection.port,
            database=connection.database,
            user=connection.username,
            password=password,
        )
        
        try:
            # Query to get tables
            query = """
                SELECT table_name, table_schema, table_type
                FROM information_schema.tables
                WHERE table_schema = $1
                ORDER BY table_name
            """
            rows = await conn.fetch(query, schema_name)
            tables = [
                Table(
                    name=row["table_name"],
                    schema=row["table_schema"],
                    table_type=row["table_type"],
                )
                for row in rows
            ]
            
            # Cache the results
            self._save_to_cache(
                connection_id=connection_id,
                metadata_type="tables",
                schema_name=schema_name,
                table_name=None,
                data=tables,
            )
            
            return tables
        finally:
            await conn.close()
    
    async def get_table_details(
        self, connection_id: int, schema_name: str, table_name: str, use_cache: bool = True
    ) -> TableDetails:
        """
        Get detailed information about a table including columns and foreign keys.
        
        Args:
            connection_id: Connection ID
            schema_name: Schema name
            table_name: Table name
            use_cache: Whether to use cached data if available
            
        Returns:
            TableDetails: Table details with columns and foreign keys
            
        Raises:
            ValueError: If connection not found
        """
        # Check cache first
        if use_cache:
            cached = self._get_from_cache(
                connection_id=connection_id,
                metadata_type="columns",
                schema_name=schema_name,
                table_name=table_name,
            )
            if cached:
                data = json.loads(cached.metadata_json)
                return TableDetails(**data)
        
        # Fetch from database
        connection = self._get_connection(connection_id)
        password = decrypt_password(connection.password_encrypted)
        
        conn = await asyncpg.connect(
            host=connection.host,
            port=connection.port,
            database=connection.database,
            user=connection.username,
            password=password,
        )
        
        try:
            # Query to get columns
            columns_query = """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = $1 AND table_name = $2
                ORDER BY ordinal_position
            """
            column_rows = await conn.fetch(columns_query, schema_name, table_name)
            columns = [
                Column(
                    name=row["column_name"],
                    data_type=row["data_type"],
                    is_nullable=row["is_nullable"] == "YES",
                    column_default=row["column_default"],
                )
                for row in column_rows
            ]
            
            # Query to get foreign keys
            fk_query = """
                SELECT
                    kcu.column_name,
                    ccu.table_name AS referenced_table,
                    ccu.column_name AS referenced_column
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = $1
                    AND tc.table_name = $2
            """
            fk_rows = await conn.fetch(fk_query, schema_name, table_name)
            foreign_keys = [
                ForeignKey(
                    column_name=row["column_name"],
                    referenced_table=row["referenced_table"],
                    referenced_column=row["referenced_column"],
                )
                for row in fk_rows
            ]
            
            # Get row count (approximate for large tables)
            count_query = f"""
                SELECT reltuples::bigint AS estimate
                FROM pg_class
                WHERE oid = '{schema_name}.{table_name}'::regclass
            """
            try:
                count_row = await conn.fetchrow(count_query)
                row_count = int(count_row["estimate"]) if count_row else None
            except:
                row_count = None
            
            table_details = TableDetails(
                name=table_name,
                schema=schema_name,
                row_count=row_count,
                columns=columns,
                foreign_keys=foreign_keys,
            )
            
            # Cache the results
            self._save_to_cache(
                connection_id=connection_id,
                metadata_type="columns",
                schema_name=schema_name,
                table_name=table_name,
                data=table_details,
            )
            
            return table_details
        finally:
            await conn.close()
    
    def refresh_metadata(self, connection_id: int) -> None:
        """
        Clear all cached metadata for a connection.
        
        Args:
            connection_id: Connection ID
        """
        self.db.query(MetadataCache).filter(
            MetadataCache.connection_id == connection_id
        ).delete()
        self.db.commit()
    
    def _get_connection(self, connection_id: int) -> Connection:
        """Get connection by ID."""
        connection = self.db.query(Connection).filter(Connection.id == connection_id).first()
        if not connection:
            raise ValueError(f"Connection with ID {connection_id} not found")
        return connection
    
    def _get_from_cache(
        self,
        connection_id: int,
        metadata_type: str,
        schema_name: str,
        table_name: Optional[str] = None,
    ) -> Optional[MetadataCache]:
        """
        Get metadata from cache if not expired.
        
        Args:
            connection_id: Connection ID
            metadata_type: Type of metadata ('schemas', 'tables', 'columns')
            schema_name: Schema name
            table_name: Table name (optional)
            
        Returns:
            Optional[MetadataCache]: Cached metadata if found and not expired
        """
        query = self.db.query(MetadataCache).filter(
            MetadataCache.connection_id == connection_id,
            MetadataCache.metadata_type == metadata_type,
            MetadataCache.schema_name == schema_name,
            MetadataCache.expires_at > datetime.utcnow(),
        )
        
        if table_name:
            query = query.filter(MetadataCache.table_name == table_name)
        else:
            query = query.filter(MetadataCache.table_name.is_(None))
        
        return query.first()
    
    def _save_to_cache(
        self,
        connection_id: int,
        metadata_type: str,
        schema_name: str,
        table_name: Optional[str],
        data: any,
    ) -> None:
        """
        Save metadata to cache.
        
        Args:
            connection_id: Connection ID
            metadata_type: Type of metadata
            schema_name: Schema name
            table_name: Table name (optional)
            data: Data to cache (will be JSON serialized)
        """
        # Delete existing cache entry
        query = self.db.query(MetadataCache).filter(
            MetadataCache.connection_id == connection_id,
            MetadataCache.metadata_type == metadata_type,
            MetadataCache.schema_name == schema_name,
        )
        
        if table_name:
            query = query.filter(MetadataCache.table_name == table_name)
        else:
            query = query.filter(MetadataCache.table_name.is_(None))
        
        query.delete()
        
        # Serialize data
        if isinstance(data, list):
            json_data = json.dumps([item.model_dump() for item in data])
        else:
            json_data = json.dumps(data.model_dump())
        
        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(hours=settings.metadata_cache_ttl_hours)
        
        # Create new cache entry
        cache_entry = MetadataCache(
            connection_id=connection_id,
            metadata_type=metadata_type,
            schema_name=schema_name,
            table_name=table_name,
            metadata_json=json_data,
            expires_at=expires_at,
        )
        
        self.db.add(cache_entry)
        self.db.commit()
