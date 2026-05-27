from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.repositories import (
    AuditRepository,
    BacktestRepository,
    ContentRepository,
    EventLogRepository,
    HaltStateRepository,
    IoTActionLogRepository,
    SchedulerRepository,
    UserRepository,
)


def _build_engine(db_file: str):
    return create_engine(
        f"sqlite:///{db_file}",
        future=True,
        connect_args={"check_same_thread": False},
    )


def test_database_models_create_expected_tables(tmp_path):
    database_path = tmp_path / "phase08_1_models.db"
    engine = _build_engine(str(database_path))
    Base.metadata.create_all(bind=engine)

    table_names = set(inspect(engine).get_table_names())
    expected_tables = {
        "users",
        "refresh_tokens",
        "audit_logs",
        "event_logs",
        "scheduler_jobs",
        "scheduler_runs",
        "halt_state",
        "backtest_results",
        "optimization_results",
        "content_items",
        "content_pipeline_runs",
        "iot_action_logs",
    }
    assert expected_tables.issubset(table_names)


def test_database_repositories_roundtrip(tmp_path):
    database_path = tmp_path / "phase08_1_repos.db"
    engine = _build_engine(str(database_path))
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        user = UserRepository(session).create(
            email="phase08.1@example.com",
            password_hash="not-a-real-secret",
            role="admin",
            display_name="Phase 08.1",
        )
        assert UUID(user.id)
        assert user.created_at is not None
        assert user.updated_at is not None

        audit_log = AuditRepository(session).create(
            actor_user_id=user.id,
            actor_email=user.email,
            action="phase08_1_model_test",
            metadata_json={"scope": "database"},
        )
        assert audit_log.metadata_json["scope"] == "database"

        event_log = EventLogRepository(session).create(
            event_type="test.event",
            source="pytest",
            message="phase08.1 repository test",
            payload={"ok": True},
        )
        assert event_log.payload_json["ok"] is True

        scheduler_repository = SchedulerRepository(session)
        job = scheduler_repository.upsert_job(
            job_id=str(uuid4()),
            name="phase08.1 job",
            job_type="backtest",
            schedule_type="interval",
            status="active",
            enabled=True,
            interval_seconds=300,
            payload_json={"symbol": "XAUUSD"},
        )
        assert job.payload_json["symbol"] == "XAUUSD"

        scheduler_run = scheduler_repository.add_run(
            job_id=job.id,
            status="completed",
            message="ok",
            output={"result": "success"},
        )
        assert scheduler_run.output_json["result"] == "success"

        halt_state = HaltStateRepository(session).set_state(
            halted=True,
            reason="test halt",
            actor="guardian",
            locked=True,
        )
        assert halt_state.halted is True
        assert halt_state.locked is True

        backtest_repository = BacktestRepository(session)
        backtest_result = backtest_repository.create_backtest_result(
            strategy="ob_aggressive",
            symbol="XAUUSD",
            timeframe="M5",
            metrics={"win_rate": 55.0},
        )
        assert backtest_result.metrics_json["win_rate"] == 55.0

        optimization_result = backtest_repository.create_optimization_result(
            strategy="ob_aggressive",
            sort_metric="profit_factor",
            ranked_results=[{"id": backtest_result.id}],
            best_result={"id": backtest_result.id},
        )
        assert optimization_result.best_result_json["id"] == backtest_result.id

        content_repository = ContentRepository(session)
        content_item = content_repository.create_content_item(
            title="Phase 08.1 test",
            topic="Safety",
            status="draft",
            approved=False,
            draft_text="draft",
            edited_text="edited",
            metadata_json={"source": "pytest"},
        )
        assert content_item.metadata_json["source"] == "pytest"

        pipeline_run = content_repository.create_pipeline_run(
            content_item_id=content_item.id,
            stage="editor",
            status="completed",
            output={"edited": True},
        )
        assert pipeline_run.output_json["edited"] is True

        iot_action = IoTActionLogRepository(session).create(
            action="power_off",
            device_alias="zdash-power-node",
            status="dry_run",
            dry_run=True,
            confirmation_required=True,
            confirmed=False,
            payload_json={"reason": "test"},
        )
        assert iot_action.payload_json["reason"] == "test"
