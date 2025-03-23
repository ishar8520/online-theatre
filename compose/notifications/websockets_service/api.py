from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status
from models import MessageModel
from services.websocket_manager import websocket_manager
from uuid import UUID


router = APIRouter()


@router.websocket('/ws/{user_uuid}')
async def websocket_endpoint(websocket: WebSocket, user_uuid: UUID):
    await websocket_manager.connect(user_uuid, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from {user_uuid}: {data}")
            await websocket_manager.handle_message(user_uuid, data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_uuid)

@router.post('/send_notification')
async def send_notification(message: MessageModel):
    user_uuid = message.user_uuid
    text = message.text
    if not await websocket_manager.send_message(user_uuid, text):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not connected')
    return {'status': 'message_sent', 'user_uuid': user_uuid}