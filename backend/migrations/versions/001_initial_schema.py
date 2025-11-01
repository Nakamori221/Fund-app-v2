"""Initial schema creation with users, cases, observations, conflicts, reports

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-11-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    user_role_enum = postgresql.ENUM(
        "analyst", "lead_partner", "ic_member", "admin",
        name="userrole",
        create_type=True
    )
    user_role_enum.create(op.get_bind())

    case_status_enum = postgresql.ENUM(
        "draft", "in_progress", "pending_review", "approved", "rejected", "closed",
        name="casestatus",
        create_type=True
    )
    case_status_enum.create(op.get_bind())

    source_tag_enum = postgresql.ENUM(
        "PUB", "EXT", "INT", "CONF", "ANL",
        name="sourcetag",
        create_type=True
    )
    source_tag_enum.create(op.get_bind())

    disclosure_level_enum = postgresql.ENUM(
        "IC", "LP", "LP_NDA", "PRIVATE",
        name="disclosurelevel",
        create_type=True
    )
    disclosure_level_enum.create(op.get_bind())

    conflict_type_enum = postgresql.ENUM(
        "price_anomaly", "data_inconsistency", "source_conflict", "timing_conflict",
        name="conflicttype",
        create_type=True
    )
    conflict_type_enum.create(op.get_bind())

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", user_role_enum, nullable=False, server_default="analyst"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # Create cases table
    op.create_table(
        "cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("sector", sa.String(255), nullable=True),
        sa.Column("status", case_status_enum, nullable=False, server_default="draft"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cases_company_name", "cases", ["company_name"])
    op.create_index("ix_cases_status_created_by", "cases", ["status", "created_by"])
    op.create_index("ix_cases_created_at", "cases", ["created_at"])

    # Create observations table
    op.create_table(
        "observations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("section", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_tag", source_tag_enum, nullable=False, server_default="PUB"),
        sa.Column("disclosure_level", disclosure_level_enum, nullable=False, server_default="PRIVATE"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("verified_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ),
        sa.ForeignKeyConstraint(["verified_by"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_observations_case_id", "observations", ["case_id"])
    op.create_index("ix_observations_case_status", "observations", ["case_id", "disclosure_level"])
    op.create_index("ix_observations_created_at", "observations", ["created_at"])
    op.create_index("ix_observations_source_tag", "observations", ["source_tag"])

    # Create conflicts table
    op.create_table(
        "conflicts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("observation_id_1", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("observation_id_2", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conflict_type", conflict_type_enum, nullable=False),
        sa.Column("severity", sa.Float(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_resolved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ),
        sa.ForeignKeyConstraint(["observation_id_1"], ["observations.id"], ),
        sa.ForeignKeyConstraint(["observation_id_2"], ["observations.id"], ),
        sa.ForeignKeyConstraint(["resolved_by"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conflicts_case_id", "conflicts", ["case_id"])
    op.create_index("ix_conflicts_case_severity", "conflicts", ["case_id", "severity"])
    op.create_index("ix_conflicts_resolved", "conflicts", ["is_resolved", "detected_at"])

    # Create reports table
    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("report_type", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", postgresql.JSON(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reports_case_id", "reports", ["case_id"])
    op.create_index("ix_reports_created_at", "reports", ["created_at"])

    # Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("resource_type", sa.String(255), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("old_values", postgresql.JSON(), nullable=True),
        sa.Column("new_values", postgresql.JSON(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(1000), nullable=True),
        sa.Column("metadata", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"])
    op.create_index("ix_audit_logs_user_action", "audit_logs", ["user_id", "action"])
    op.create_index("ix_audit_logs_resource", "audit_logs", ["resource_type", "resource_id"])


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table("audit_logs")
    op.drop_table("reports")
    op.drop_table("conflicts")
    op.drop_table("observations")
    op.drop_table("cases")
    op.drop_table("users")

    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS conflicttype CASCADE")
    op.execute("DROP TYPE IF EXISTS disclosurelevel CASCADE")
    op.execute("DROP TYPE IF EXISTS sourcetag CASCADE")
    op.execute("DROP TYPE IF EXISTS casestatus CASCADE")
    op.execute("DROP TYPE IF EXISTS userrole CASCADE")
