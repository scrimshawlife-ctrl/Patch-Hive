"""Add canonical immutable hierarchy and operational records.

Revision ID: 20240927_canon_alignment
Revises: 20240926_acceptance_features
"""

import sqlalchemy as sa
from alembic import op


revision = "20240927_canon_alignment"
down_revision = "20240926_acceptance_features"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rig_revisions",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("rig_id", sa.Integer(), nullable=False),
        sa.Column("previous_revision_id", sa.String(64), nullable=True),
        sa.Column("schema_version", sa.String(64), nullable=False),
        sa.Column("canonical_rig", sa.JSON(), nullable=False),
        sa.Column("canonical_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["rig_id"], ["racks.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["previous_revision_id"], ["rig_revisions.id"], ondelete="RESTRICT"
        ),
    )
    op.create_index("ix_rig_revisions_rig_id", "rig_revisions", ["rig_id"])

    op.create_table(
        "generation_runs",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rig_revision_id", sa.String(64), nullable=False),
        sa.Column("schema_version", sa.String(64), nullable=False),
        sa.Column("generator_version", sa.String(64), nullable=False),
        sa.Column("generation_seed", sa.Integer(), nullable=False),
        sa.Column("normalized_input_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["rig_revision_id"], ["rig_revisions.id"], ondelete="RESTRICT"
        ),
    )
    op.create_index("ix_generation_runs_user_id", "generation_runs", ["user_id"])
    op.create_index(
        "ix_generation_runs_rig_revision_id", "generation_runs", ["rig_revision_id"]
    )

    op.create_table(
        "patch_libraries",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("run_id", sa.String(64), nullable=False, unique=True),
        sa.Column("artifact_manifest_hash", sa.String(64), nullable=False),
        sa.Column("canonical_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["generation_runs.id"], ondelete="RESTRICT"),
    )

    op.create_table(
        "generated_patches",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("patch_library_id", sa.String(64), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("patch_graph", sa.JSON(), nullable=False),
        sa.Column("patch_plan", sa.JSON(), nullable=False),
        sa.Column("validation_report", sa.JSON(), nullable=False),
        sa.Column("variations", sa.JSON(), nullable=False),
        sa.Column("canonical_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["patch_library_id"], ["patch_libraries.id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("patch_library_id", "position"),
    )
    op.create_index(
        "ix_generated_patches_patch_library_id", "generated_patches", ["patch_library_id"]
    )

    op.create_table(
        "user_patch_annotations",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("patch_id", sa.String(64), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("favorite", sa.Boolean(), nullable=False),
        sa.Column("tried", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patch_id"], ["generated_patches.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "patch_id"),
    )

    op.create_table(
        "module_revisions",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("module_id", sa.Integer(), nullable=False),
        sa.Column("previous_revision_id", sa.String(64), nullable=True),
        sa.Column("schema_version", sa.String(64), nullable=False),
        sa.Column("spec", sa.JSON(), nullable=False),
        sa.Column("canonical_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["module_id"], ["modules.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["previous_revision_id"], ["module_revisions.id"], ondelete="RESTRICT"
        ),
    )

    op.create_table(
        "stage_receipts",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("run_id", sa.String(64), nullable=False),
        sa.Column("stage", sa.String(100), nullable=False),
        sa.Column("operation", sa.String(150), nullable=False),
        sa.Column("operation_version", sa.String(64), nullable=False),
        sa.Column("determinism_class", sa.String(40), nullable=False),
        sa.Column("input_hash", sa.String(64), nullable=False),
        sa.Column("output_hash", sa.String(64), nullable=False),
        sa.Column("receipt", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["generation_runs.id"], ondelete="RESTRICT"),
    )

    op.create_table(
        "artifact_manifests",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("run_id", sa.String(64), nullable=False, unique=True),
        sa.Column("manifest", sa.JSON(), nullable=False),
        sa.Column("canonical_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["generation_runs.id"], ondelete="RESTRICT"),
    )

    op.create_table(
        "generation_jobs",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("request_id", sa.String(64), nullable=False, unique=True),
        sa.Column("run_id", sa.String(64), nullable=False, unique=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("error_code", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("attempts >= 0", name="ck_generation_jobs_attempts"),
        sa.ForeignKeyConstraint(["run_id"], ["generation_runs.id"], ondelete="RESTRICT"),
    )

    op.create_table(
        "canonical_exports",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("source_run_id", sa.String(64), nullable=False),
        sa.Column("source_rig_revision_id", sa.String(64), nullable=False),
        sa.Column("artifact_manifest_hash", sa.String(64), nullable=False),
        sa.Column("export_version", sa.String(64), nullable=False),
        sa.Column("license", sa.String(100), nullable=False),
        sa.Column("credit_cost", sa.Integer(), nullable=False),
        sa.Column("ledger_entry_id", sa.String(64), nullable=True, unique=True),
        sa.Column("idempotency_key", sa.String(128), nullable=False, unique=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("credit_cost >= 0", name="ck_canonical_exports_cost"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["source_run_id"], ["generation_runs.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["source_rig_revision_id"], ["rig_revisions.id"], ondelete="RESTRICT"
        ),
    )

    op.create_table(
        "canonical_credit_ledger",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("delta", sa.Integer(), nullable=False),
        sa.Column("entry_type", sa.String(20), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False, unique=True),
        sa.Column("export_id", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["export_id"], ["canonical_exports.id"], ondelete="RESTRICT"),
    )

    op.create_table(
        "stripe_event_records",
        sa.Column("stripe_event_id", sa.String(128), primary_key=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("payload_hash", sa.String(64), nullable=False),
        sa.Column("livemode", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "canonical_admin_audit_events",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("actor_user_id", sa.Integer(), nullable=False),
        sa.Column("actor_role", sa.String(30), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target_type", sa.String(100), nullable=False),
        sa.Column("target_id", sa.String(100), nullable=False),
        sa.Column("before_hash", sa.String(64), nullable=True),
        sa.Column("after_hash", sa.String(64), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="RESTRICT"),
    )


def downgrade() -> None:
    for table in (
        "canonical_admin_audit_events",
        "stripe_event_records",
        "canonical_credit_ledger",
        "canonical_exports",
        "generation_jobs",
        "artifact_manifests",
        "stage_receipts",
        "module_revisions",
        "user_patch_annotations",
        "generated_patches",
        "patch_libraries",
        "generation_runs",
        "rig_revisions",
    ):
        op.drop_table(table)
