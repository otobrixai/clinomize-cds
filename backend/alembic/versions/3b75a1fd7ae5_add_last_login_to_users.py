"""add_last_login_to_users

Revision ID: 3b75a1fd7ae5
Revises: 625daa822b41
Create Date: 2026-01-16 01:34:51.742515

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3b75a1fd7ae5'  # Replace with actual from filename
down_revision = '625daa822b41'  # This is your current revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add last_login column to users table
    op.add_column('users', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))
    
    # Also add other missing columns if needed
    op.add_column('users', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))


def downgrade() -> None:
    op.drop_column('users', 'version')
    op.drop_column('users', 'last_login')