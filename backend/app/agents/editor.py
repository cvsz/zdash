from app.agents.base import Agent


class EditorAgent(Agent):
    def __init__(self) -> None:
        super().__init__(name='Editor', role='Content Editor Agent')
