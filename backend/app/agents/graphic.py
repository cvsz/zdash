from app.agents.base import Agent


class GraphicAgent(Agent):
    def __init__(self) -> None:
        super().__init__(name='Graphic', role='Graphic Generation Agent')
