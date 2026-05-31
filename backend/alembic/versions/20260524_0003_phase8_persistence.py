"""phase8 persistence and auth

Revision ID: 20260524_0003
Revises:
Create Date: 2026-05-24
"""

from alembic import op
import sqlalchemy as sa
from typing import Any


revision = '20260524_0003'
down_revision = None
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    return bool(sa.inspect(op.get_bind()).has_table(table_name))


def _create_table_once(table_name: str, *columns: Any, **kwargs: Any) -> None:
    if _table_exists(table_name):
        return
    _create_table_once(table_name, *columns, **kwargs)


def upgrade() -> None:
    _create_table_once(
        'agents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    _create_table_once(
        'messages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('sender', sa.String(), nullable=False),
        sa.Column('target', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    _create_table_once(
        'events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    _create_table_once(
        'trading_signals',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('timeframe', sa.String(), nullable=False),
        sa.Column('direction', sa.String(), nullable=False),
        sa.Column('strategy', sa.String(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    _create_table_once(
        'execution_attempts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('mode', sa.String(), nullable=False),
        sa.Column('executed', sa.Boolean(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    _create_table_once(
        'risk_decisions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('decision_type', sa.String(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('immutable', sa.Boolean(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    _create_table_once(
        'halt_flags',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('halted', sa.Boolean(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('locked', sa.Boolean(), nullable=False),
        sa.Column('actor', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    _create_table_once(
        'scheduler_jobs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('interval_seconds', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    _create_table_once(
        'backtest_runs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('strategy', sa.String(), nullable=False),
        sa.Column('risk_per_trade', sa.Float(), nullable=False),
        sa.Column('primary_candidate', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    _create_table_once(
        'backtest_results',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('run_id', sa.String(), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    _create_table_once(
        'content_items',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('topic', sa.String(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('state', sa.String(), nullable=False),
        sa.Column('approved', sa.Boolean(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    _create_table_once(
        'audit_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('actor', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('target', sa.String(), nullable=False),
        sa.Column('detail', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    _create_table_once(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
    )

    _create_table_once(
        'live_mode_approvals',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('approved', sa.Boolean(), nullable=False),
        sa.Column('actor', sa.String(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    for table in [
        'live_mode_approvals',
        'users',
        'audit_logs',
        'content_items',
        'backtest_results',
        'backtest_runs',
        'scheduler_jobs',
        'halt_flags',
        'risk_decisions',
        'execution_attempts',
        'trading_signals',
        'events',
        'messages',
        'agents',
    ]:
        if _table_exists(table):
            op.drop_table(table)
