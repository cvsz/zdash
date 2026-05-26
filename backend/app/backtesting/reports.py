from app.backtesting.models import BacktestResult, OptimizationResult


class BacktestReportBuilder:
    def build_summary(self, result: BacktestResult) -> dict:
        return {
            "result_id": result.id,
            "strategy": result.strategy,
            "dataset": result.request.dataset,
            "symbol": result.symbol,
            "timeframe": result.timeframe,
            "parameters": result.parameters,
            "metrics": result.metrics.model_dump(mode="json"),
            "warnings": result.warnings,
            "risk_notes": [
                "Research, simulation, and paper-trading validation only.",
                "Strategy promotion does not enable live trading.",
                "Guardian and global safety controls remain mandatory.",
            ],
            "disclaimer": "Backtest results are not guaranteed future performance.",
        }

    def build_markdown_report(self, result: BacktestResult) -> str:
        metrics = result.metrics
        return (
            "# Backtest Report\n\n"
            f"- Result ID: `{result.id}`\n"
            f"- Strategy: `{result.strategy}`\n"
            f"- Dataset: `{result.request.dataset}`\n"
            f"- Symbol / Timeframe: `{result.symbol}` / `{result.timeframe}`\n"
            f"- Trades: `{metrics.total_trades}`\n"
            f"- Win Rate: `{metrics.win_rate}%`\n"
            f"- Net Profit %: `{metrics.net_profit_percent}%`\n"
            f"- Profit Factor: `{metrics.profit_factor}`\n"
            f"- Max Drawdown %: `{metrics.max_drawdown_percent}%`\n\n"
            "## Parameters\n\n"
            f"`{result.parameters}`\n\n"
            "## Warnings\n\n"
            f"{result.warnings or ['none']}\n\n"
            "> For research/simulation/paper-trading validation only.\n"
            "> Backtest results are not guaranteed future performance."
        )

    def build_optimization_summary(self, result: OptimizationResult) -> dict:
        best_result = result.best_result
        return {
            "optimization_id": result.id,
            "sort_metric": result.sort_metric,
            "executed_combinations": result.executed_combinations,
            "total_combinations": result.total_combinations,
            "best_result_id": best_result.id if best_result else None,
            "best_strategy": best_result.strategy if best_result else None,
            "best_net_profit_percent": best_result.metrics.net_profit_percent if best_result else None,
            "best_profit_factor": best_result.metrics.profit_factor if best_result else None,
            "warnings": result.warnings,
        }
