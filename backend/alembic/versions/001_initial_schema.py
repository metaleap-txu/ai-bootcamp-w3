"""Initial database schema for connections, metadata_cache, and query_history.

Revision ID: 001
Revises: 
Create Date: 2025-12-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database tables."""
    
    # Create connections table
    op.create_table(
        'connections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('host', sa.String(length=255), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('database', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('password_encrypted', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_connections_name', 'connections', ['name'], unique=True)
    
    # Create metadata_cache table
    op.create_table(
        'metadata_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('connection_id', sa.Integer(), nullable=False),
        sa.Column('schema_name', sa.String(length=255), nullable=False),
        sa.Column('table_name', sa.String(length=255), nullable=True),
        sa.Column('metadata_type', sa.String(length=50), nullable=False),
        sa.Column('metadata_json', sa.Text(), nullable=False),
        sa.Column('cached_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['connection_id'], ['connections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_metadata_cache_connection', 'metadata_cache', ['connection_id'])
    op.create_index(
        'ix_metadata_cache_lookup',
        'metadata_cache',
        ['connection_id', 'schema_name', 'table_name', 'metadata_type']
    )
    
    # Create query_history table
    op.create_table(
        'query_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('connection_id', sa.Integer(), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('executed_at', sa.DateTime(), nullable=False),
        sa.Column('execution_time_ms', sa.Integer(), nullable=False),
        sa.Column('row_count', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['connection_id'], ['connections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_query_history_connection', 'query_history', ['connection_id'])
    op.create_index('ix_query_history_executed_at', 'query_history', ['executed_at'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index('ix_query_history_executed_at', table_name='query_history')
    op.drop_index('ix_query_history_connection', table_name='query_history')
    op.drop_table('query_history')
    
    op.drop_index('ix_metadata_cache_lookup', table_name='metadata_cache')
    op.drop_index('ix_metadata_cache_connection', table_name='metadata_cache')
    op.drop_table('metadata_cache')
    
    op.drop_index('ix_connections_name', table_name='connections')
    op.drop_table('connections')
