"""Create complaint status history and feedback tables

Revision ID: 0004_citizen_tables
Revises: 0003_postgis_location
Create Date: 2026-11-17 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0004_citizen_tables'
down_revision = '0003_postgis_location'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create complaint_status_history table
    op.create_table(
        'complaint_status_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('complaint_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('changed_by', sa.Integer(), nullable=True),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_complaint_status_history_id'), 'complaint_status_history', ['id'], unique=False)
    op.create_index(op.f('ix_complaint_status_history_complaint_id'), 'complaint_status_history', ['complaint_id'], unique=False)

    # Create complaint_feedback table
    op.create_table(
        'complaint_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('complaint_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('complaint_id')
    )
    op.create_index(op.f('ix_complaint_feedback_id'), 'complaint_feedback', ['id'], unique=False)
    op.create_index(op.f('ix_complaint_feedback_complaint_id'), 'complaint_feedback', ['complaint_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_complaint_feedback_complaint_id'), table_name='complaint_feedback')
    op.drop_index(op.f('ix_complaint_feedback_id'), table_name='complaint_feedback')
    op.drop_table('complaint_feedback')
    op.drop_index(op.f('ix_complaint_status_history_complaint_id'), table_name='complaint_status_history')
    op.drop_index(op.f('ix_complaint_status_history_id'), table_name='complaint_status_history')
    op.drop_table('complaint_status_history')
