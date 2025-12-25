"""
Service layer for database connection management.

This module handles the business logic for PostgreSQL database connections including:
- CRUD operations (Create, Read, Update, Delete)
- Connection testing with asyncpg
- Password encryption/decryption using Fernet symmetric encryption
- Tracking last tested timestamps for connection health monitoring

All passwords are encrypted before storing in SQLite using environment-configured encryption keys.
"""
from typing import List, Optional

import asyncpg
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.connection import Connection
from src.schemas.connection import (
    ConnectionCreate,
    ConnectionUpdate,
    ConnectionTestResponse,
)
from src.utils.security import encrypt_password, decrypt_password


class ConnectionService:
    """Service for managing database connections."""
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
    
    def get_all(self) -> List[Connection]:
        """
        Get all connections.
        
        Returns:
            List[Connection]: List of all connections
        """
        return self.db.query(Connection).order_by(Connection.created_at.desc()).all()
    
    def get_by_id(self, connection_id: int) -> Optional[Connection]:
        """
        Get connection by ID.
        
        Args:
            connection_id: Connection ID
            
        Returns:
            Optional[Connection]: Connection if found, None otherwise
        """
        return self.db.query(Connection).filter(Connection.id == connection_id).first()
    
    def get_by_name(self, name: str) -> Optional[Connection]:
        """
        Get connection by name.
        
        Args:
            name: Connection name
            
        Returns:
            Optional[Connection]: Connection if found, None otherwise
        """
        return self.db.query(Connection).filter(Connection.name == name).first()
    
    def create(self, connection_data: ConnectionCreate) -> Connection:
        """
        Create a new connection.
        
        Args:
            connection_data: Connection creation data
            
        Returns:
            Connection: Created connection
            
        Raises:
            ValueError: If connection with name already exists
        """
        # Check if name already exists
        existing = self.get_by_name(connection_data.name)
        if existing:
            raise ValueError(f"Connection with name '{connection_data.name}' already exists")
        
        # Encrypt password
        encrypted_password = encrypt_password(connection_data.password)
        
        # Create connection
        connection = Connection(
            name=connection_data.name,
            host=connection_data.host,
            port=connection_data.port,
            database=connection_data.database,
            username=connection_data.username,
            password_encrypted=encrypted_password,
            description=connection_data.description,
        )
        
        try:
            self.db.add(connection)
            self.db.commit()
            self.db.refresh(connection)
            return connection
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to create connection: {str(e)}") from e
    
    def update(self, connection_id: int, update_data: ConnectionUpdate) -> Optional[Connection]:
        """
        Update an existing connection.
        
        Args:
            connection_id: Connection ID
            update_data: Connection update data
            
        Returns:
            Optional[Connection]: Updated connection if found, None otherwise
            
        Raises:
            ValueError: If updated name conflicts with existing connection
        """
        connection = self.get_by_id(connection_id)
        if not connection:
            return None
        
        # Check name uniqueness if name is being updated
        if update_data.name and update_data.name != connection.name:
            existing = self.get_by_name(update_data.name)
            if existing:
                raise ValueError(f"Connection with name '{update_data.name}' already exists")
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Handle password encryption if password is being updated
        if "password" in update_dict:
            update_dict["password_encrypted"] = encrypt_password(update_dict.pop("password"))
        
        for field, value in update_dict.items():
            setattr(connection, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(connection)
            return connection
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to update connection: {str(e)}") from e
    
    def delete(self, connection_id: int) -> bool:
        """
        Delete a connection.
        
        Args:
            connection_id: Connection ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        connection = self.get_by_id(connection_id)
        if not connection:
            return False
        
        self.db.delete(connection)
        self.db.commit()
        return True
    
    async def test_connection(
        self,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
    ) -> ConnectionTestResponse:
        """
        Test database connection using asyncpg.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            username: Database username
            password: Database password
            
        Returns:
            ConnectionTestResponse: Test result
        """
        try:
            # Attempt to connect
            conn = await asyncpg.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password,
                timeout=10.0,  # 10 second timeout
            )
            
            # Test with simple query
            await conn.fetchval("SELECT 1")
            
            # Close connection
            await conn.close()
            
            return ConnectionTestResponse(
                success=True,
                message="Connection successful"
            )
        except asyncpg.PostgresError as e:
            return ConnectionTestResponse(
                success=False,
                message="PostgreSQL connection failed",
                error=str(e)
            )
        except Exception as e:
            return ConnectionTestResponse(
                success=False,
                message="Connection failed",
                error=str(e)
            )
    
    async def test_connection_by_id(self, connection_id: int) -> ConnectionTestResponse:
        """
        Test an existing connection by ID.
        
        Args:
            connection_id: Connection ID
            
        Returns:
            ConnectionTestResponse: Test result
            
        Raises:
            ValueError: If connection not found
        """
        connection = self.get_by_id(connection_id)
        if not connection:
            raise ValueError(f"Connection with ID {connection_id} not found")
        
        # Decrypt password
        password = decrypt_password(connection.password_encrypted)
        
        # Test connection
        return await self.test_connection(
            host=connection.host,
            port=connection.port,
            database=connection.database,
            username=connection.username,
            password=password,
        )
