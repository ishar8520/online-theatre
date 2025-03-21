from __future__ import annotations

import enum
import uuid

from fastapi import (
    APIRouter,
)
from pydantic import BaseModel

from ....services.auth import (
    AuthServiceDep,
)
from ....tasks import send_notification_task

router = APIRouter()


class NotificationType(enum.StrEnum):
    EMAIL = 'email'
    SMS = 'sms'
    PUSH = 'push'


class Notification(BaseModel):
    user_id: uuid.UUID | None = None
    subject: str | None = None
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
async def send_notification(auth_service: AuthServiceDep,
                            notification: Notification) -> SendNotificationResponse:
    if notification.user_id is None:
        return SendNotificationResponse()

    user = await auth_service.get_user(user_id=notification.user_id)
    if user is None:
        return SendNotificationResponse()

    await send_notification_task.kiq(user=user)

    return SendNotificationResponse()
