def selection_report(strategy: str, metrics: dict) -> str:
    return (
        f"Selected strategy '{strategy}' with win_rate={metrics['win_rate']}%, "
        f"profit_factor={metrics['profit_factor']}, max_drawdown={metrics['max_drawdown']}%."
    )
