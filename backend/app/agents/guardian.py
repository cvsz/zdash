from app.agents.base import Agent


class GuardianAgent(Agent):
    def __init__(self) -> None:
        super().__init__(name='Guardian', role='Risk Guardian')
