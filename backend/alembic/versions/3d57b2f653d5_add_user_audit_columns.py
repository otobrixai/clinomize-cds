"""add_user_audit_columns

Revision ID: 3d57b2f653d5
Revises: 3b75a1fd7ae5
Create Date: 2026-01-16 01:52:45.482308

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d57b2f653d5'
down_revision = '3b75a1fd7ae5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to users table
    op.add_column('users', sa.Column('created_by', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('updated_by', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('deleted_by', sa.Integer(), nullable=True))
    
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_users_created_by', 'users', 'users',
        ['created_by'], ['id']
    )
    op.create_foreign_key(
        'fk_users_updated_by', 'users', 'users',
        ['updated_by'], ['id']
    )
    op.create_foreign_key(
        'fk_users_deleted_by', 'users', 'users',
        ['deleted_by'], ['id']
    )


def downgrade() -> None:
    # Remove in reverse order
    op.drop_constraint('fk_users_deleted_by', 'users', type_='foreignkey')
    op.drop_constraint('fk_users_updated_by', 'users', type_='foreignkey')
    op.drop_constraint('fk_users_created_by', 'users', type_='foreignkey')
    
    op.drop_column('users', 'deleted_by')
    op.drop_column('users', 'deleted_at')
    op.drop_column('users', 'updated_by')
    op.drop_column('users', 'created_by')