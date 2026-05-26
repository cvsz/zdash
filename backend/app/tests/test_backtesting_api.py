from app.api import backtesting as backtesting_api
from app.backtesting.models import BacktestRequest, OptimizationRequest


def _assert_envelope(payload: dict) -> None:
    assert set(payload.keys()) == {"ok", "data", "error", "timestamp"}


def test_get_backtesting_status() -> None:
    body = backtesting_api.status()
    _assert_envelope(body)
    assert "enabled" in body["data"]


def test_get_backtesting_strategies() -> None:
    body = backtesting_api.strategies()
    _assert_envelope(body)
    assert body["ok"] is True
    assert body["data"]["strategies"]


def test_post_backtesting_run_and_results() -> None:
    run_body = backtesting_api.run(BacktestRequest(strategy="ob_aggressive"))
    _assert_envelope(run_body)
    assert run_body["ok"] is True
    result_id = run_body["data"]["result"]["id"]

    list_body = backtesting_api.results()
    _assert_envelope(list_body)
    assert list_body["ok"] is True
    assert list_body["data"]["results"]

    detail_body = backtesting_api.result(result_id)
    _assert_envelope(detail_body)
    assert detail_body["ok"] is True
    assert detail_body["data"]["result"]["id"] == result_id


def test_post_backtesting_optimize_and_optimizations() -> None:
    optimize_body = backtesting_api.optimize(
        OptimizationRequest(
            strategy="ob_aggressive",
            parameter_grid={"lookback": [8, 12], "risk_reward": [1.5, 2.0]},
            max_combinations=4,
        )
    )
    _assert_envelope(optimize_body)
    assert optimize_body["ok"] is True

    list_body = backtesting_api.optimizations()
    _assert_envelope(list_body)
    assert list_body["ok"] is True
    assert list_body["data"]["optimizations"]


def test_promotion_check_and_report_endpoints() -> None:
    run_body = backtesting_api.run(BacktestRequest(strategy="ob_aggressive"))
    result_id = run_body["data"]["result"]["id"]

    promotion_body = backtesting_api.promotion(result_id)
    _assert_envelope(promotion_body)
    assert promotion_body["ok"] is True
    assert "approved" in promotion_body["data"]["decision"]

    report_body = backtesting_api.report(result_id)
    _assert_envelope(report_body)
    assert report_body["ok"] is True
    assert "markdown_report" in report_body["data"]
