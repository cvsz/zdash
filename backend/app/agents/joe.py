from app.agents.base import Agent


class JoeAgent(Agent):
    def __init__(self) -> None:
        super().__init__(name='Joe', role='Backtesting and Strategy Lab Agent')
