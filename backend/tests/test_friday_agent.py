from app.agents.registry import bootstrap_agents, registry
from app.api import agents
from app.core.events import event_bus
from app.scheduler.models import CreateJobRequest, JobType, ScheduleType


def _assert_envelope(payload: dict) -> None:
    assert set(payload.keys()) == {"ok", "data", "error", "timestamp"}


def test_friday_agent_is_registered() -> None:
    bootstrap_agents()
    body = agents.list_agents()
    _assert_envelope(body)
    ids = {row["id"] for row in body["data"]["agents"]}
    assert "friday" in ids


def test_friday_lists_jobs() -> None:
    bootstrap_agents()
    friday = registry.get("friday")
    assert friday is not None

    result = friday.run_task("list_jobs")
    assert result["ok"] is True
    assert isinstance(result["jobs"], list)


def test_friday_can_run_manual_job() -> None:
    bootstrap_agents()
    friday = registry.get("friday")
    assert friday is not None

    created = friday.create_job(
        CreateJobRequest(
            name="friday-manual-health",
            job_type=JobType.health_check,
            schedule_type=ScheduleType.manual,
            payload={},
        )
    )
    run = friday.run_job(created.id)
    assert run.ok is True
    assert run.status == "completed"


def test_friday_emits_events() -> None:
    bootstrap_agents()
    friday = registry.get("friday")
    assert friday is not None

    event_bus.clear()
    friday.run_task("list_jobs")

    types = [event.type for event in event_bus.list_events(limit=50)]
    assert "friday.command.completed" in types
