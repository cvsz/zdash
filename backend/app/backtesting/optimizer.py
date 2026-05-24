from app.backtesting.strategy_lab import StrategyLab


class Optimizer:
    def __init__(self) -> None:
        self.lab = StrategyLab()

    def sweep(self, strategy: str, risks: list[float]) -> list[dict]:
        rows: list[dict] = []
        for risk in risks:
            result = self.lab.run(strategy_name=strategy, risk_per_trade=risk)
            rows.append({'risk_per_trade': risk, **result})
        rows.sort(key=lambda r: (r['profit_factor'], r['win_rate']), reverse=True)
        return rows
