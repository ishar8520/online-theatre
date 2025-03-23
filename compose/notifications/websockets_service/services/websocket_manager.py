from fastapi import WebSocket
from typing import Dict, Optional
import asyncio

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.pending_confirmations: Dict[str, asyncio.Future] = {}

    async def connect(self, user_uuid: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_uuid] = websocket

    def disconnect(self, user_uuid: str):
        if user_uuid in self.active_connections:
            del self.active_connections[user_uuid]

    async def send_message(self, user_uuid: str, message: str, timeout: int = 5) -> bool:
        if user_uuid not in self.active_connections:
            return False

        websocket = self.active_connections[user_uuid]
        if websocket:
            await websocket.send_text(message)
            return True

    async def handle_message(self, user_uuid: str, message: str):
        if user_uuid in self.pending_confirmations:
            if message == '{"status": "received"}':
                self.pending_confirmations[user_uuid].set_result(True)
            else:
                self.pending_confirmations[user_uuid].set_result(False)

websocket_manager = WebSocketManager()