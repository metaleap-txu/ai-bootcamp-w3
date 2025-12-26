"""Add export_history table for export operation audit trail.

Revision ID: 003
Revises: 002
Create Date: 2025-12-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create export_history table."""
    
    op.create_table(
        'export_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('query_history_id', sa.Integer(), nullable=True),
        sa.Column('format', sa.String(length=10), nullable=False),
        sa.Column('row_count', sa.Integer(), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('exported_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(['query_history_id'], ['query_history.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("format IN ('csv', 'json')", name='ck_export_history_format'),
        sa.CheckConstraint("status IN ('success', 'failed', 'cancelled')", name='ck_export_history_status'),
        sa.CheckConstraint("row_count >= 0", name='ck_export_history_row_count'),
        sa.CheckConstraint("file_size_bytes >= 0", name='ck_export_history_file_size')
    )
    op.create_index('ix_export_history_user_id', 'export_history', ['user_id'])
    op.create_index('ix_export_history_exported_at', 'export_history', ['exported_at'], postgresql_ops={'exported_at': 'DESC'})
    op.create_index('ix_export_history_status', 'export_history', ['status'])


def downgrade() -> None:
    """Drop export_history table."""
    op.drop_index('ix_export_history_status', table_name='export_history')
    op.drop_index('ix_export_history_exported_at', table_name='export_history')
    op.drop_index('ix_export_history_user_id', table_name='export_history')
    op.drop_table('export_history')
