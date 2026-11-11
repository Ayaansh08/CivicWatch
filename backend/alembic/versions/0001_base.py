"""
Base migration: creates users, categories, departments, complaints tables
and seeds 4 initial categories.

TEAMMATES: Use down_revision="0001_base" for your own migrations so they
run after this one.

Revision ID: 0001_base
Revises: (none — this is the first migration)
Create Date: 2026-11-12
"""
from alembic import op
import sqlalchemy as sa

# Alembic uses these to chain migrations in order
revision = "0001_base"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables and seed the categories lookup table."""

    # Create the users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="citizen"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # Create the categories lookup table
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
    )

    # Create the departments lookup table
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
    )

    # Create the complaints table (references users, categories, departments)
    op.create_table(
        "complaints",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", sa.Integer(),
                  sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False,
                  server_default="Submitted"),
        sa.Column("priority", sa.String(50), nullable=False,
                  server_default="Medium"),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("photo_path", sa.String(500), nullable=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("users.id"), nullable=False),
        sa.Column("department_id", sa.Integer(),
                  sa.ForeignKey("departments.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("NOW()")),
    )

    # Seed the 4 initial categories that the project plan specifies
    op.bulk_insert(
        sa.table(
            "categories",
            sa.column("name", sa.String),
        ),
        [
            {"name": "Pothole"},
            {"name": "Garbage"},
            {"name": "Water Leakage"},
            {"name": "Streetlight"},
        ],
    )


def downgrade() -> None:
    """Drop all tables in reverse order to respect foreign key constraints."""
    # Drop the table that has the most foreign keys first
    op.drop_table("complaints")
    op.drop_table("departments")
    op.drop_table("categories")
    op.drop_table("users")
