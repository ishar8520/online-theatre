import asyncio
from typing import Dict

from fastapi import HTTPException, WebSocket, status
from services.auth_manager import auth_client


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.pending_confirmations: Dict[str, asyncio.Future] = {}

    async def connect(self, user_uuid: str, websocket: WebSocket):
        if not await auth_client.verify_user(user_uuid):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authorized")
        await websocket.accept()
        self.active_connections[user_uuid] = websocket

    def disconnect(self, user_uuid: str):
        if user_uuid in self.active_connections:
            del self.active_connections[user_uuid]

    async def send_message(self, user_uuid: str, message: str, timeout: int = 5) -> bool:
        if user_uuid not in self.active_connections:
            return False

        websocket = self.active_connections[user_uuid]
        await websocket.send_text(message)
        print(f"Message sent to {user_uuid}: {message}")

        confirmation_future = asyncio.get_event_loop().create_future()
        self.pending_confirmations[user_uuid] = confirmation_future

        try:
            await asyncio.wait_for(confirmation_future, timeout=timeout)
            print(f"Confirmation received from {user_uuid}")
            return True
        except asyncio.TimeoutError:
            print(f"Confirmation timeout for {user_uuid}")
            return False
        finally:
            if user_uuid in self.pending_confirmations:
                del self.pending_confirmations[user_uuid]

    async def handle_message(self, user_uuid: str, message: str):
        if user_uuid in self.pending_confirmations:
            if message == '{"status": "received"}':
                self.pending_confirmations[user_uuid].set_result(True)
            else:
                self.pending_confirmations[user_uuid].set_result(False)


websocket_manager = WebSocketManager()
