from app.agents.joe import JoeAgent
from app.agents.registry import bootstrap_agents, registry
from app.backtesting.models import BacktestRequest
from app.core.events import event_bus


def test_joe_agent_is_registered() -> None:
    bootstrap_agents()
    joe = registry.get("joe")
    assert joe is not None
    assert joe.id == "joe"


def test_joe_lists_strategies() -> None:
    joe = JoeAgent()
    strategies = joe.list_strategies()
    names = {item["name"] for item in strategies}
    assert "ob_aggressive" in names
    assert "ob_conservative" in names
    assert "trend_follow" in names


def test_joe_can_run_backtest() -> None:
    joe = JoeAgent()
    result = joe.run_backtest(BacktestRequest(strategy="ob_aggressive"))
    assert result.strategy == "ob_aggressive"
    assert result.metrics.total_trades >= 0


def test_joe_emits_events() -> None:
    joe = JoeAgent()
    event_bus.clear()
    joe.run_backtest(BacktestRequest(strategy="ob_aggressive"))
    event_types = {event.type for event in event_bus.list_events(limit=1000)}
    assert "joe.command.received" in event_types
    assert "joe.command.completed" in event_types
