"""Tests for worker task execution."""

from unittest.mock import MagicMock, patch

import pytest

from app.workers.models import WorkerTask
from app.workers.tasks import run_task


@pytest.fixture
def sample_task() -> WorkerTask:
    """Create a sample worker task."""
    return WorkerTask(
        organization_id="test_org",
        workspace_id="test_workspace",
        task_type="risk_check",
        payload={"balance": 10000, "equity": 9500},
    )


def test_run_risk_check_task(sample_task: WorkerTask) -> None:
    """Test running a risk check task."""
    with patch("app.workers.tasks.get_guardian_service") as mock_guardian:
        mock_decision = MagicMock()
        mock_decision.model_dump.return_value = {"action": "allow", "risk_level": "low"}
        mock_guardian.return_value.check.return_value = mock_decision

        result = run_task(sample_task)

        assert result["ok"] is True
        assert result["task_type"] == "risk_check"
        assert "decision" in result
        mock_guardian.return_value.check.assert_called_once()


def test_run_backtest_task() -> None:
    """Test running a backtest task."""
    task = WorkerTask(
        organization_id="test_org",
        workspace_id="test_workspace",
        task_type="backtest_run",
        payload={"strategy": "trend_follow", "symbol": "EURUSD"},
    )

    with patch("app.workers.tasks.get_backtest_service") as mock_backtest:
        mock_result = MagicMock()
        mock_result.id = "backtest_123"
        mock_backtest.return_value.run_backtest.return_value = mock_result

        result = run_task(task)

        assert result["ok"] is True
        assert result["task_type"] == "backtest_run"
        assert result["result_id"] == "backtest_123"


def test_run_content_pipeline_task() -> None:
    """Test running a content pipeline task."""
    task = WorkerTask(
        organization_id="test_org",
        workspace_id="test_workspace",
        task_type="content_pipeline_run",
        payload={"topic": "Market analysis"},
    )

    with patch("app.workers.tasks.get_content_pipeline") as mock_pipeline:
        mock_result = MagicMock()
        mock_result.id = "content_456"
        mock_pipeline.return_value.run_full_pipeline.return_value = mock_result

        result = run_task(task)

        assert result["ok"] is True
        assert result["task_type"] == "content_pipeline_run"
        assert result["run_id"] == "content_456"


def test_run_notification_dispatch_task() -> None:
    """Test running a notification dispatch task."""
    task = WorkerTask(
        organization_id="test_org",
        workspace_id="test_workspace",
        task_type="notification_dispatch",
        payload={
            "actor_user_id": "user_123",
            "title": "Test Alert",
            "message": "This is a test",
        },
    )

    with patch("app.workers.tasks.get_notification_service") as mock_notify:
        mock_notification = {"id": "notif_789", "status": "sent"}
        mock_notify.return_value.send_test_notification.return_value = mock_notification

        result = run_task(task)

        assert result["ok"] is True
        assert result["task_type"] == "notification_dispatch"
        assert result["notification"] == mock_notification


def test_run_unsupported_task_type() -> None:
    """Test the defensive fallback for a task that bypasses schema validation."""
    task = WorkerTask.model_construct(
        organization_id="test_org",
        workspace_id="test_workspace",
        task_type="unknown_task",
        payload={},
    )

    result = run_task(task)

    assert result["ok"] is False
    assert result["task_type"] == "unknown_task"
    assert result["error"] == "unsupported task type"


def test_run_dry_run_tasks() -> None:
    """Test tasks that always return dry-run results."""
    dry_run_tasks = [
        "optimization_run",
        "content_publish_dry_run",
        "iot_status_check",
        "trading_scan",
        "audit_compaction",
        "backup_run",
    ]

    for task_type in dry_run_tasks:
        task = WorkerTask(
            organization_id="test_org",
            workspace_id="test_workspace",
            task_type=task_type,  # type: ignore[arg-type]
            payload={},
        )

        result = run_task(task)

        assert result["ok"] is True
        assert result["task_type"] == task_type
