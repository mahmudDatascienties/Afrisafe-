"""Initial schema: users and prediction_history.

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-23
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("lga", sa.String(100), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("gender", sa.String(20), nullable=False),
        sa.Column("phone_number", sa.String(20), nullable=True),
        sa.Column("role", sa.String(20), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"])

    op.create_table(
        "prediction_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("prediction", sa.String(50), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("risk", sa.String(30), nullable=False),
        sa.Column("recommendation", sa.String(500), nullable=False),
        sa.Column("advice", sa.JSON(), nullable=False),
        sa.Column("symptoms", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_prediction_history_id", "prediction_history", ["id"])
    op.create_index("ix_prediction_history_user_id", "prediction_history", ["user_id"])
    op.create_index("ix_prediction_history_risk", "prediction_history", ["risk"])


def downgrade() -> None:
    op.drop_index("ix_prediction_history_risk", table_name="prediction_history")
    op.drop_index("ix_prediction_history_user_id", table_name="prediction_history")
    op.drop_index("ix_prediction_history_id", table_name="prediction_history")
    op.drop_table("prediction_history")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
