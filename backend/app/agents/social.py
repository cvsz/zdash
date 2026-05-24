from app.agents.base import Agent


class SocialAgent(Agent):
    def __init__(self) -> None:
        super().__init__(name='Social', role='Social Publishing Agent')
