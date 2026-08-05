"""reconcile auth persistence schema

Revision ID: 20260805_0001
Revises: 20260531_0001
Create Date: 2026-08-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260805_0001"
down_revision: str | None = "20260531_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _inspector() -> sa.Inspector:
    return sa.inspect(op.get_bind())


def _dialect_name() -> str:
    return op.get_bind().dialect.name


def _table_exists(table_name: str) -> bool:
    return bool(_inspector().has_table(table_name))


def _column_exists(table_name: str, column_name: str) -> bool:
    if not _table_exists(table_name):
        return False
    return any(
        column["name"] == column_name
        for column in _inspector().get_columns(table_name)
    )


def _add_column_once(table_name: str, column: sa.Column) -> None:
    if not _column_exists(table_name, str(column.name)):
        op.add_column(table_name, column)


def _set_default(
    table_name: str,
    column_name: str,
    existing_type: sa.types.TypeEngine,
    default: sa.sql.elements.TextClause | None,
) -> None:
    # SQLite cannot alter a column default without recreating the table.
    # The ORM also supplies client-side timestamp defaults, so the migration
    # remains safe for SQLite test databases while PostgreSQL receives the
    # authoritative database-level defaults used in production.
    if _dialect_name() == "sqlite":
        return
    op.alter_column(
        table_name,
        column_name,
        existing_type=existing_type,
        existing_nullable=False,
        server_default=default,
    )


def upgrade() -> None:
    now = sa.text("CURRENT_TIMESTAMP")

    if _table_exists("users"):
        op.execute(
            sa.text(
                "UPDATE users "
                "SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP)"
            )
        )
        if _column_exists("users", "updated_at"):
            op.execute(
                sa.text(
                    "UPDATE users "
                    "SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)"
                )
            )
        _set_default("users", "created_at", sa.DateTime(timezone=True), now)
        if _column_exists("users", "updated_at"):
            _set_default("users", "updated_at", sa.DateTime(timezone=True), now)

    if not _table_exists("audit_logs"):
        return

    _add_column_once(
        "audit_logs",
        sa.Column("actor_user_id", sa.String(), nullable=False, server_default=""),
    )
    _add_column_once(
        "audit_logs",
        sa.Column("actor_email", sa.String(), nullable=False, server_default=""),
    )
    _add_column_once(
        "audit_logs",
        sa.Column("resource_type", sa.String(), nullable=False, server_default=""),
    )
    _add_column_once(
        "audit_logs",
        sa.Column("resource_id", sa.String(), nullable=False, server_default=""),
    )
    _add_column_once(
        "audit_logs",
        sa.Column("result", sa.String(), nullable=False, server_default="success"),
    )
    _add_column_once(
        "audit_logs",
        sa.Column("ip_address", sa.String(), nullable=False, server_default=""),
    )
    _add_column_once(
        "audit_logs",
        sa.Column("user_agent", sa.String(), nullable=False, server_default=""),
    )
    _add_column_once(
        "audit_logs",
        sa.Column(
            "metadata",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
    )
    _add_column_once(
        "audit_logs",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=now,
        ),
    )

    if _column_exists("audit_logs", "actor"):
        op.execute(
            sa.text(
                "UPDATE audit_logs SET actor_email = actor "
                "WHERE actor_email = '' AND actor IS NOT NULL"
            )
        )
    if _column_exists("audit_logs", "target"):
        op.execute(
            sa.text(
                "UPDATE audit_logs SET resource_id = target "
                "WHERE resource_id = '' AND target IS NOT NULL"
            )
        )
    if _column_exists("audit_logs", "detail"):
        op.execute(
            sa.text(
                "UPDATE audit_logs SET metadata = detail "
                "WHERE detail IS NOT NULL"
            )
        )

    op.execute(
        sa.text(
            "UPDATE audit_logs "
            "SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP), "
            "updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)"
        )
    )

    _set_default("audit_logs", "created_at", sa.DateTime(timezone=True), now)
    _set_default("audit_logs", "updated_at", sa.DateTime(timezone=True), now)

    # Retain legacy columns for rollback/data compatibility, but make them
    # safe for inserts produced by the current ORM model.
    if _column_exists("audit_logs", "actor"):
        _set_default("audit_logs", "actor", sa.String(), sa.text("''"))
    if _column_exists("audit_logs", "role"):
        _set_default("audit_logs", "role", sa.String(), sa.text("''"))
    if _column_exists("audit_logs", "target"):
        _set_default("audit_logs", "target", sa.String(), sa.text("''"))
    if _column_exists("audit_logs", "detail"):
        _set_default("audit_logs", "detail", sa.JSON(), sa.text("'{}'"))


def downgrade() -> None:
    if _table_exists("users"):
        _set_default(
            "users", "created_at", sa.DateTime(timezone=True), None
        )
        if _column_exists("users", "updated_at"):
            _set_default(
                "users", "updated_at", sa.DateTime(timezone=True), None
            )

    if not _table_exists("audit_logs"):
        return

    for column_name, column_type in (
        ("actor", sa.String()),
        ("role", sa.String()),
        ("target", sa.String()),
        ("detail", sa.JSON()),
        ("created_at", sa.DateTime(timezone=True)),
    ):
        if _column_exists("audit_logs", column_name):
            _set_default("audit_logs", column_name, column_type, None)

    for column_name in (
        "updated_at",
        "metadata",
        "user_agent",
        "ip_address",
        "result",
        "resource_id",
        "resource_type",
        "actor_email",
        "actor_user_id",
    ):
        if _column_exists("audit_logs", column_name):
            op.drop_column("audit_logs", column_name)
