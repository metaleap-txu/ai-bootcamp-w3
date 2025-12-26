"""Add export_preferences table for user export settings.

Revision ID: 002
Revises: 001
Create Date: 2025-12-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create export_preferences table."""
    
    op.create_table(
        'export_preferences',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('default_format', sa.String(length=10), nullable=False, server_default='csv'),
        sa.Column('include_metadata', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('pretty_json', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('csv_include_bom', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('user_id'),
        sa.CheckConstraint("default_format IN ('csv', 'json')", name='ck_export_preferences_format')
    )


def downgrade() -> None:
    """Drop export_preferences table."""
    op.drop_table('export_preferences')
