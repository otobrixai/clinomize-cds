"""add_analytics_and_cost_tables

Revision ID: 625daa822b41
Revises: 16e11639992a
Create Date: 2026-01-15 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '625daa822b41'
down_revision = '16e11639992a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create blood_product_cost table - for hospital-specific pricing
    op.create_table('blood_product_cost',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=False),
        sa.Column('component_type', sa.String(length=50), nullable=False),
        sa.Column('unit_cost_bdt', sa.Float(), nullable=False),
        sa.Column('units_per_bag', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('hospital_id', 'component_type', name='uq_hospital_component')
    )
    
    # 2. Create analytics_monthly_summary table - pre-aggregated for performance
    op.create_table('analytics_monthly_summary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=False),
        sa.Column('summary_date', sa.Date(), nullable=False),  # First day of month
        sa.Column('total_encounters', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_recommendations', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('guideline_compliant', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_overrides', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rbc_recommended', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rbc_actual', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('platelets_recommended', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('platelets_actual', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ffp_recommended', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ffp_actual', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cryo_recommended', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cryo_actual', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('estimated_savings_bdt', sa.Float(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('hospital_id', 'summary_date', name='uq_hospital_monthly_summary')
    )
    
    # 3. Add cost tracking to recommendations table (nullable, backward compatible)
    op.add_column('recommendations', sa.Column('estimated_cost_bdt', sa.Float(), nullable=True))
    op.add_column('recommendations', sa.Column('actual_cost_bdt', sa.Float(), nullable=True))
    
    # 4. Create index for faster analytics queries
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    op.create_index('ix_recommendations_created_at', 'recommendations', ['created_at'])
    op.create_index('ix_recommendations_component', 'recommendations', ['component'])


def downgrade() -> None:
    # Remove in reverse order
    op.drop_index('ix_recommendations_component', table_name='recommendations')
    op.drop_index('ix_recommendations_created_at', table_name='recommendations')
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    
    op.drop_column('recommendations', 'actual_cost_bdt')
    op.drop_column('recommendations', 'estimated_cost_bdt')
    
    op.drop_table('analytics_monthly_summary')
    op.drop_table('blood_product_cost')