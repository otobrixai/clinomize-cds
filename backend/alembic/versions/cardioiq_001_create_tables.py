"""
Database migration script for CardioIQ tables
Run this to create the CardioIQ database schema
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'cardioiq_001'
down_revision = '625daa822b41'  # Points to latest existing migration (analytics and cost tables)
branch_labels = None
depends_on = None



def upgrade():
    # Create cardioiq_encounters table
    op.create_table(
        'cardioiq_encounters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=True),
        sa.Column('patient_id', sa.String(), nullable=True),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('sex', sa.String(length=10), nullable=False),
        sa.Column('weight_kg', sa.Float(), nullable=False),
        sa.Column('chest_pain', sa.Boolean(), nullable=False),
        sa.Column('chest_pain_type', sa.String(length=20), nullable=True),
        sa.Column('dyspnea', sa.Boolean(), nullable=True),
        sa.Column('syncope', sa.Boolean(), nullable=True),
        sa.Column('sbp', sa.Integer(), nullable=False),
        sa.Column('hr', sa.Integer(), nullable=False),
        sa.Column('spo2', sa.Integer(), nullable=False),
        sa.Column('st_elevation', sa.Boolean(), nullable=True),
        sa.Column('st_depression', sa.Boolean(), nullable=True),
        sa.Column('t_wave_inversion', sa.Boolean(), nullable=True),
        sa.Column('non_diagnostic_ecg', sa.Boolean(), nullable=True),
        sa.Column('ecg_confidence', sa.String(length=10), nullable=True),
        sa.Column('troponin_status', sa.String(length=20), nullable=False),
        sa.Column('troponin_positive', sa.Boolean(), nullable=True),
        sa.Column('troponin_value', sa.Float(), nullable=True),
        sa.Column('creatinine', sa.Float(), nullable=True),
        sa.Column('potassium', sa.Float(), nullable=True),
        sa.Column('history_cad', sa.Boolean(), nullable=True),
        sa.Column('history_diabetes', sa.Boolean(), nullable=True),
        sa.Column('history_hypertension', sa.Boolean(), nullable=True),
        sa.Column('history_ckd', sa.Boolean(), nullable=True),
        sa.Column('history_heart_failure', sa.Boolean(), nullable=True),
        sa.Column('history_stroke', sa.Boolean(), nullable=True),
        sa.Column('on_beta_blocker', sa.Boolean(), nullable=True),
        sa.Column('on_digoxin', sa.Boolean(), nullable=True),
        sa.Column('on_qt_prolonging_drugs', sa.Boolean(), nullable=True),
        sa.Column('care_setting', sa.String(length=10), nullable=False),
        sa.Column('has_cath_lab', sa.Boolean(), nullable=True),
        sa.Column('can_transfer_pci', sa.Boolean(), nullable=True),
        sa.Column('has_troponin', sa.Boolean(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cardioiq_encounters_id'), 'cardioiq_encounters', ['id'], unique=False)
    op.create_index(op.f('ix_cardioiq_encounters_patient_id'), 'cardioiq_encounters', ['patient_id'], unique=False)

    # Create cardioiq_recommendations table
    op.create_table(
        'cardioiq_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('encounter_id', sa.Integer(), nullable=False),
        sa.Column('clinical_category', sa.String(length=100), nullable=False),
        sa.Column('recommended_level_of_care', sa.String(length=20), nullable=False),
        sa.Column('risk_scores', sa.JSON(), nullable=True),
        sa.Column('recommended_actions', sa.JSON(), nullable=False),
        sa.Column('safety_warnings', sa.JSON(), nullable=True),
        sa.Column('cost_flags', sa.JSON(), nullable=True),
        sa.Column('rationale_summary', sa.JSON(), nullable=True),
        sa.Column('guideline_links', sa.JSON(), nullable=True),
        sa.Column('rule_hits', sa.JSON(), nullable=False),
        sa.Column('rule_version', sa.String(length=20), nullable=False),
        sa.Column('engine_version', sa.String(length=20), nullable=False),
        sa.Column('actual_level_of_care', sa.String(length=20), nullable=True),
        sa.Column('recommendation_followed', sa.Boolean(), nullable=True),
        sa.Column('outcome_notes', sa.Text(), nullable=True),
        sa.Column('outcome_recorded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('outcome_recorded_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['encounter_id'], ['cardioiq_encounters.id'], ),
        sa.ForeignKeyConstraint(['outcome_recorded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('encounter_id')
    )
    op.create_index(op.f('ix_cardioiq_recommendations_id'), 'cardioiq_recommendations', ['id'], unique=False)

    # Create cardioiq_audit_logs table
    op.create_table(
        'cardioiq_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('encounter_id', sa.Integer(), nullable=False),
        sa.Column('recommendation_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rule_version', sa.String(length=20), nullable=True),
        sa.Column('action_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['encounter_id'], ['cardioiq_encounters.id'], ),
        sa.ForeignKeyConstraint(['recommendation_id'], ['cardioiq_recommendations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cardioiq_audit_logs_id'), 'cardioiq_audit_logs', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_cardioiq_audit_logs_id'), table_name='cardioiq_audit_logs')
    op.drop_table('cardioiq_audit_logs')
    op.drop_index(op.f('ix_cardioiq_recommendations_id'), table_name='cardioiq_recommendations')
    op.drop_table('cardioiq_recommendations')
    op.drop_index(op.f('ix_cardioiq_encounters_patient_id'), table_name='cardioiq_encounters')
    op.drop_index(op.f('ix_cardioiq_encounters_id'), table_name='cardioiq_encounters')
    op.drop_table('cardioiq_encounters')
