"""phase47 team workspace models

Revision ID: 20260531_0001
Revises: 7054888e2a84
Create Date: 2026-05-31
"""

from typing import Any, Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260531_0001"
down_revision: Union[str, None] = "7054888e2a84"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    return bool(sa.inspect(op.get_bind()).has_table(table_name))


def _create_table_once(table_name: str, *columns: Any, **kwargs: Any) -> None:
    if _table_exists(table_name):
        return
    op.create_table(table_name, *columns, **kwargs)


def upgrade() -> None:
    _create_table_once(
        "team_members",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False, index=True),
        sa.Column("workspace_id", sa.String(), nullable=True),
        sa.Column("user_id", sa.String(), nullable=True, index=True),
        sa.Column("email", sa.String(), nullable=False, index=True),
        sa.Column("display_name", sa.String(), nullable=False, server_default=""),
        sa.Column("role", sa.String(), nullable=False, server_default="viewer"),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    _create_table_once(
        "team_invitations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False, index=True),
        sa.Column("workspace_id", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=False, index=True),
        sa.Column("role", sa.String(), nullable=False, server_default="viewer"),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("invited_by", sa.String(), nullable=False, server_default=""),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    _create_table_once(
        "team_workspace_access",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False, index=True),
        sa.Column("workspace_id", sa.String(), nullable=False, index=True),
        sa.Column("member_id", sa.String(), nullable=False, index=True),
        sa.Column("access_level", sa.String(), nullable=False, server_default="read"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    _create_table_once(
        "team_agent_assignments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False, index=True),
        sa.Column("workspace_id", sa.String(), nullable=False, index=True),
        sa.Column("member_id", sa.String(), nullable=True, index=True),
        sa.Column("agent_id", sa.String(), nullable=False, index=True),
        sa.Column("assignment_role", sa.String(), nullable=False, server_default="observer"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    for table in [
        "team_agent_assignments",
        "team_workspace_access",
        "team_invitations",
        "team_members",
    ]:
        if _table_exists(table):
            op.drop_table(table)
