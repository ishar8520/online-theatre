from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status
from models import MessageModel
from services.websocket_manager import websocket_manager
import logging

logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.websocket('/ws/{token}')
async def websocket_endpoint(websocket: WebSocket, token: str):
    user_uuid = await websocket_manager.connect(token, websocket)
    logging.info(f'User connect {user_uuid}')
    print(f'User connect {user_uuid}')
    try:
        while True:
            data = await websocket.receive_text()
            logging.info(f'Received from {user_uuid}: {data}')
            await websocket_manager.handle_message(user_uuid, data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_uuid)
        logging.info(f'Client {user_uuid} disconnected')


@router.post('/send_notification/{user_uuid}')
async def send_notification(message: MessageModel):
    user_uuid = message.user_uuid
    text = message.text
    if not await websocket_manager.send_message(user_uuid, text):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not connected')
    logging.info(f'Message sent to {user_uuid}: {text}')
    return {'status': 'message_sent', 'user_uuid': user_uuid}
