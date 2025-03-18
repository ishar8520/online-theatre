from __future__ import annotations

import enum
import uuid

from fastapi import (
    APIRouter,
)
from pydantic import BaseModel

router = APIRouter()


class NotificationType(enum.StrEnum):
    EMAIL = 'email'
    SMS = 'sms'
    PUSH = 'push'


class Notification(BaseModel):
    user_id: uuid.UUID | None = None
    subject: str
    text: str | None = None
    template_id: uuid.UUID | None = None
    template_context: dict | None = None
    type: NotificationType = NotificationType.EMAIL


class SendNotificationResponse(BaseModel):
    pass


@router.post(
    '/send/',
    name='notifications:send',
    response_model=SendNotificationResponse,
)
async def send_notification(_notification: Notification) -> SendNotificationResponse:
    return SendNotificationResponse()
