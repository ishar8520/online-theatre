import asyncio
from typing import Dict
import json

from fastapi import HTTPException, WebSocket, status
from services.auth_manager import auth_client
import logging

logging.basicConfig(level=logging.INFO)


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.pending_confirmations: Dict[str, asyncio.Future] = {}

    async def connect(self, token: str, websocket: WebSocket):
        try:
            validate_body_json = await auth_client.verify_user(token)
            if not validate_body_json:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authorized")
            validate_body = json.loads(validate_body_json)
            await websocket.accept()
            self.active_connections[validate_body["id"]] = websocket
            return validate_body["id"]
        except Exception as e:
            logging.error(e)


    def disconnect(self, user_uuid: str):
        if user_uuid in self.active_connections:
            del self.active_connections[user_uuid]

    async def send_message(self, user_uuid: str, message: str, timeout: int = 5) -> bool:
        if user_uuid not in self.active_connections:
            return False

        websocket = self.active_connections[user_uuid]
        await websocket.send_text(message)
        logging.info(f"Message sent to {user_uuid}: {message}")

        confirmation_future = asyncio.get_event_loop().create_future()
        self.pending_confirmations[user_uuid] = confirmation_future

        try:
            await asyncio.wait_for(confirmation_future, timeout=timeout)
            logging.info(f"Confirmation received from {user_uuid}")
            return True
        except asyncio.TimeoutError:
            logging.info(f"Confirmation timeout for {user_uuid}")
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
