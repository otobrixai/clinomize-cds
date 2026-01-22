"""add_server_default_to_updated_at

Revision ID: acc3c26feed3
Revises: 086e8141a439
Create Date: 2026-01-21 23:46:16.969957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acc3c26feed3'
down_revision = '086e8141a439'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add server_default to hospitals.updated_at
    op.alter_column('hospitals', 'updated_at',
               server_default=sa.func.now(),
               existing_type=sa.DateTime(),
               nullable=False)
               
    # Add server_default to users.updated_at (prevent similar issue)
    op.alter_column('users', 'updated_at',
               server_default=sa.func.now(),
               existing_type=sa.DateTime(),
               nullable=False)


def downgrade() -> None:
    # Remove server_default from hospitals.updated_at
    op.alter_column('hospitals', 'updated_at',
               server_default=None,
               existing_type=sa.DateTime(),
               nullable=False)

    # Remove server_default from users.updated_at
    op.alter_column('users', 'updated_at',
               server_default=None,
               existing_type=sa.DateTime(),
               nullable=False)
