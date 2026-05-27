class WebsocketManager:
    def __init__(self):
        self.connections = []

    async def connect(self, ws):
        await ws.accept()
        self.connections.append(ws)

    def disconnect(self, ws):
        if ws in self.connections:
            self.connections.remove(ws)


manager = WebsocketManager()
