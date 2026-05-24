from app.agents.base import Agent


class FridayAgent(Agent):
    def __init__(self) -> None:
        super().__init__(name='Friday', role='Scheduler Automation Agent')
