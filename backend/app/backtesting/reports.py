from app.backtesting.models import BacktestResult, OptimizationResult


class BacktestReportBuilder:
    def build_summary(self, result: BacktestResult) -> dict:
        return {"strategy": result.strategy, "dataset": result.request.dataset, "symbol": result.symbol, "timeframe": result.timeframe, "parameters": result.parameters, "metrics": result.metrics.model_dump(), "warnings": result.warnings, "risk_notes": "For research/simulation only.", "disclaimer": "Past performance does not guarantee future performance."}

    def build_markdown_report(self, result: BacktestResult) -> str:
        return f"# Backtest Report\n\nStrategy: {result.strategy}\nDataset: {result.request.dataset}\nSymbol/TF: {result.symbol}/{result.timeframe}\nNet Profit %: {result.metrics.net_profit_percent}\n\n> Results are for research/simulation only and are not guaranteed future performance."

    def build_optimization_summary(self, result: OptimizationResult) -> dict:
        return {"sort_metric": result.sort_metric, "executed_combinations": result.executed_combinations, "total_combinations": result.total_combinations, "best_result_id": result.best_result.id if result.best_result else None, "warnings": result.warnings}
