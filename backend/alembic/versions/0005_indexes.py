"""Add performance indexes on the complaints table.

Merge this PR LAST so the revision chain stays linear.

Revision ID: 0005_indexes
Revises: 0004_citizen_tables
Create Date: 2026-11-19 04:00:00.000000
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '0005_indexes'
down_revision = '0004_citizen_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Index on complaint status for filtering by workflow state
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_complaints_status ON complaints (status)"
    )
    # Index on category_id for filtering complaints by category
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_complaints_category_id ON complaints (category_id)"
    )
    # Index on created_at for time-based sorting and range queries
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_complaints_created_at ON complaints (created_at)"
    )
    # Index on user_id for fetching all complaints by a specific citizen
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_complaints_user_id ON complaints (user_id)"
    )
    # Index on department_id for fetching complaints assigned to a department
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_complaints_department_id ON complaints (department_id)"
    )


def downgrade() -> None:
    # Drop the five complaint indexes added in upgrade()
    op.execute("DROP INDEX IF EXISTS ix_complaints_status")
    op.execute("DROP INDEX IF EXISTS ix_complaints_category_id")
    op.execute("DROP INDEX IF EXISTS ix_complaints_created_at")
    op.execute("DROP INDEX IF EXISTS ix_complaints_user_id")
    op.execute("DROP INDEX IF EXISTS ix_complaints_department_id")
