
from typing import List, Optional
from fastapi import WebSocket
from pydantic import BaseModel

class Data(BaseModel):
    userId: Optional[str] = None

class WebSocketData(BaseModel):
    key: str
    data: Data

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections = [conn for conn in self.active_connections if conn != websocket]

    async def send_message(self, data: WebSocketData):
        json_data = data.json()
        for connection in self.active_connections:
            await connection.send_text(json_data)

    async def broadcast_message(self, data: WebSocketData):
        json_data = data.json()
        for connection in self.active_connections:
            await connection.send_text(json_data)
