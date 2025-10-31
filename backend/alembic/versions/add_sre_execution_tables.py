"""Add SRE execution tracking tables

Revision ID: add_sre_execution_tables
Revises: previous_migration
Create Date: 2025-10-30 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_sre_execution_tables'
down_revision = 'previous_migration'  # Update this to your latest migration
branch_labels = None
depends_on = None


def upgrade():
    # Create sre_incident_execution table
    op.create_table('sre_incident_execution',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_number', sa.String(length=50), nullable=False),
        sa.Column('incident_title', sa.String(length=500), nullable=True),
        sa.Column('incident_description', sa.Text(), nullable=True),
        sa.Column('target_ip', sa.String(length=45), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('assignment_group', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('agent_name', sa.String(length=100), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_summary', sa.Text(), nullable=True),
        sa.Column('final_hypothesis', sa.Text(), nullable=True),
        sa.Column('resolution_steps', sa.JSON(), nullable=True),
        sa.Column('verification_results', sa.JSON(), nullable=True),
        sa.Column('servicenow_payload', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sre_incident_execution_id'), 'sre_incident_execution', ['id'], unique=False)
    op.create_index(op.f('ix_sre_incident_execution_incident_number'), 'sre_incident_execution', ['incident_number'], unique=False)
    op.create_unique_constraint(None, 'sre_incident_execution', ['incident_number'])
    
    # Create incident_execution_log table
    op.create_table('incident_execution_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_number', sa.String(length=50), nullable=False),
        sa.Column('agent_name', sa.String(length=100), nullable=False),
        sa.Column('step', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('hypothesis', sa.Text(), nullable=True),
        sa.Column('command_executed', sa.Text(), nullable=True),
        sa.Column('command_output', sa.Text(), nullable=True),
        sa.Column('verification', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('provenance', sa.JSON(), nullable=True),
        sa.Column('incident_execution_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['incident_execution_id'], ['sre_incident_execution.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incident_execution_log_id'), 'incident_execution_log', ['id'], unique=False)
    op.create_index(op.f('ix_incident_execution_log_incident_number'), 'incident_execution_log', ['incident_number'], unique=False)
    
    # Create sre_timeline_entry table
    op.create_table('sre_timeline_entry',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_execution_id', sa.Integer(), nullable=False),
        sa.Column('step_number', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['incident_execution_id'], ['sre_incident_execution.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sre_timeline_entry_id'), 'sre_timeline_entry', ['id'], unique=False)
    
    # Create sre_hypothesis table
    op.create_table('sre_hypothesis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_execution_id', sa.Integer(), nullable=False),
        sa.Column('hypothesis_text', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Integer(), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('supporting_evidence', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['incident_execution_id'], ['sre_incident_execution.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sre_hypothesis_id'), 'sre_hypothesis', ['id'], unique=False)
    
    # Create sre_verification table
    op.create_table('sre_verification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_execution_id', sa.Integer(), nullable=False),
        sa.Column('verification_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('command_executed', sa.Text(), nullable=True),
        sa.Column('expected_result', sa.Text(), nullable=True),
        sa.Column('actual_result', sa.Text(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['incident_execution_id'], ['sre_incident_execution.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sre_verification_id'), 'sre_verification', ['id'], unique=False)
    
    # Create sre_evidence table
    op.create_table('sre_evidence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_execution_id', sa.Integer(), nullable=False),
        sa.Column('evidence_type', sa.String(length=50), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('collected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('relevance_score', sa.Integer(), nullable=True),
        sa.Column('incident_execution_id_ref', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sre_evidence_id'), 'sre_evidence', ['id'], unique=False)
    
    # Create sre_provenance table
    op.create_table('sre_provenance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_execution_id', sa.Integer(), nullable=False),
        sa.Column('step_id', sa.String(length=100), nullable=False),
        sa.Column('parent_step_id', sa.String(length=100), nullable=True),
        sa.Column('reasoning_type', sa.String(length=50), nullable=False),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('reasoning_process', sa.Text(), nullable=True),
        sa.Column('output_conclusion', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('agent_component', sa.String(length=100), nullable=True),
        sa.Column('incident_execution_id_ref', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['incident_execution_id'], ['sre_incident_execution.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sre_provenance_id'), 'sre_provenance', ['id'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_sre_provenance_id'), table_name='sre_provenance')
    op.drop_table('sre_provenance')
    
    op.drop_index(op.f('ix_sre_evidence_id'), table_name='sre_evidence')
    op.drop_table('sre_evidence')
    
    op.drop_index(op.f('ix_sre_verification_id'), table_name='sre_verification')
    op.drop_table('sre_verification')
    
    op.drop_index(op.f('ix_sre_hypothesis_id'), table_name='sre_hypothesis')
    op.drop_table('sre_hypothesis')
    
    op.drop_index(op.f('ix_sre_timeline_entry_id'), table_name='sre_timeline_entry')
    op.drop_table('sre_timeline_entry')
    
    op.drop_index(op.f('ix_incident_execution_log_incident_number'), table_name='incident_execution_log')
    op.drop_index(op.f('ix_incident_execution_log_id'), table_name='incident_execution_log')
    op.drop_table('incident_execution_log')
    
    op.drop_constraint(None, 'sre_incident_execution', type_='unique')
    op.drop_index(op.f('ix_sre_incident_execution_incident_number'), table_name='sre_incident_execution')
    op.drop_index(op.f('ix_sre_incident_execution_id'), table_name='sre_incident_execution')
    op.drop_table('sre_incident_execution')