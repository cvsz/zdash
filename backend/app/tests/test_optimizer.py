from app.backtesting.models import OptimizationRequest
from app.backtesting.optimizer import ParameterOptimizer
from app.backtesting.strategy_lab import StrategyLab


def test_grid_expansion() -> None:
    optimizer = ParameterOptimizer()
    combos = optimizer.expand_grid({"a": [1, 2], "b": [3, 4]})
    assert len(combos) == 4
    assert {"a": 1, "b": 3} in combos


def test_max_combinations_cap() -> None:
    optimizer = ParameterOptimizer()
    request = OptimizationRequest(
        strategy="ob_aggressive",
        parameter_grid={"lookback": [8, 10, 12], "risk_reward": [1.5, 2.0, 2.5]},
        max_combinations=4,
    )
    result = optimizer.optimize(request)
    assert result.total_combinations == 9
    assert result.executed_combinations == 4
    assert result.warnings


def test_optimization_ranks_results() -> None:
    optimizer = ParameterOptimizer(StrategyLab())
    request = OptimizationRequest(
        strategy="ob_aggressive",
        parameter_grid={"lookback": [8, 12], "risk_reward": [1.5, 2.0]},
        max_combinations=4,
        sort_metric="profit_factor",
    )
    result = optimizer.optimize(request)
    assert result.ranked_results
    sorted_values = [item.metrics.profit_factor for item in result.ranked_results]
    assert sorted_values == sorted(sorted_values, reverse=True)


def test_unsupported_sort_metric_defaults_safely() -> None:
    optimizer = ParameterOptimizer()
    request = OptimizationRequest(
        strategy="ob_aggressive",
        parameter_grid={"lookback": [8, 12]},
        sort_metric="unknown_metric",
        max_combinations=2,
    )
    result = optimizer.optimize(request)
    assert result.sort_metric == "profit_factor"
    assert any("Unsupported sort metric" in warning for warning in result.warnings)
