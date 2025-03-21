from __future__ import annotations

from fastapi import (
    APIRouter,
)
from pydantic import BaseModel

from ....services.notifications import Notification
from ....tasks import send_notification_task

router = APIRouter()


class SendNotificationResponse(BaseModel):
    pass


@router.post(
    '/send/',
    name='notifications:send',
    response_model=SendNotificationResponse,
)
async def send_notification(notification: Notification) -> SendNotificationResponse:
    await send_notification_task.kiq(notification=notification)

    return SendNotificationResponse()
