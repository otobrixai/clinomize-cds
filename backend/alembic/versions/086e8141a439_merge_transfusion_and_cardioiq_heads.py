"""merge transfusion and cardioiq heads

Revision ID: 086e8141a439
Revises: 04fd5180e68a, cardioiq_001
Create Date: 2026-01-21 23:04:53.158958

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '086e8141a439'
down_revision = ('04fd5180e68a', 'cardioiq_001')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
