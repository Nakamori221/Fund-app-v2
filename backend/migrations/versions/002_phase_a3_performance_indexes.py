"""Phase A3: Performance optimization indexes for users and audit_logs

Revision ID: 002_phase_a3_performance_indexes
Revises: 001_initial_schema
Create Date: 2025-11-02

This migration adds optimized indexes to improve query performance:
- User table: role, created_at, role+is_active, created_at+is_active
- AuditLog table: resource_id, action, resource_type+resource_id+timestamp
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "002_phase_a3_performance_indexes"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add optimized indexes for performance improvement"""

    # ==========================================
    # User Table Indexes
    # ==========================================

    # Index 1: role column (frequently used in filtering)
    op.create_index(
        "idx_users_role",
        "users",
        ["role"],
        if_not_exists=True,
    )

    # Index 2: created_at DESC (for latest users query)
    op.create_index(
        "idx_users_created_at_desc",
        "users",
        ["created_at"],
        postgresql_using="DESC" if op.get_context().dialect.name == "postgresql" else None,
        if_not_exists=True,
    )

    # Index 3: Composite index for role + is_active (common filter combination)
    op.create_index(
        "idx_users_role_is_active",
        "users",
        ["role", "is_active"],
        if_not_exists=True,
    )

    # Index 4: Composite index for created_at + is_active
    op.create_index(
        "idx_users_created_at_is_active",
        "users",
        ["created_at", "is_active"],
        postgresql_using="DESC" if op.get_context().dialect.name == "postgresql" else None,
        if_not_exists=True,
    )

    # ==========================================
    # AuditLog Table Indexes
    # ==========================================

    # Index 1: resource_id (for resource history queries)
    op.create_index(
        "idx_audit_logs_resource_id",
        "audit_logs",
        ["resource_id"],
        if_not_exists=True,
    )

    # Index 2: action (for action-based aggregation)
    op.create_index(
        "idx_audit_logs_action",
        "audit_logs",
        ["action"],
        if_not_exists=True,
    )

    # Index 3: Composite index for resource_type + resource_id + timestamp DESC
    # This is critical for efficient resource history retrieval with proper ordering
    op.create_index(
        "idx_audit_logs_resource_type_timestamp",
        "audit_logs",
        ["resource_type", "resource_id", "timestamp"],
        postgresql_using="DESC" if op.get_context().dialect.name == "postgresql" else None,
        if_not_exists=True,
    )

    # Index 4: Composite index for is_deleted filtering (soft delete queries)
    op.create_index(
        "idx_audit_logs_is_deleted_timestamp",
        "audit_logs",
        ["is_deleted", "timestamp"],
        if_not_exists=True,
    )


def downgrade() -> None:
    """Remove the added indexes"""

    # Drop User table indexes
    op.drop_index("idx_users_role", table_name="users", if_exists=True)
    op.drop_index("idx_users_created_at_desc", table_name="users", if_exists=True)
    op.drop_index("idx_users_role_is_active", table_name="users", if_exists=True)
    op.drop_index("idx_users_created_at_is_active", table_name="users", if_exists=True)

    # Drop AuditLog table indexes
    op.drop_index("idx_audit_logs_resource_id", table_name="audit_logs", if_exists=True)
    op.drop_index("idx_audit_logs_action", table_name="audit_logs", if_exists=True)
    op.drop_index("idx_audit_logs_resource_type_timestamp", table_name="audit_logs", if_exists=True)
    op.drop_index("idx_audit_logs_is_deleted_timestamp", table_name="audit_logs", if_exists=True)
