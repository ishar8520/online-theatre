from __future__ import annotations

from fastapi import (
    APIRouter,
)
from pydantic import BaseModel
from taskiq import AsyncTaskiqTask

from ....services.notifications import (
    TextNotification,
    TemplateNotification,
)
from ....tasks import (
    send_text_notification_task,
    send_text_notifications_bulk_task,
    send_template_notification_task,
    send_template_notifications_bulk_task,
)

router = APIRouter()


class SendNotificationResponse(BaseModel):
    task_id: str


@router.post(
    '/send/text',
    name='notifications:send-text',
    response_model=SendNotificationResponse,
)
async def send_text_notification(notification: TextNotification) -> SendNotificationResponse:
    task: AsyncTaskiqTask[None] = await send_text_notification_task.kiq(  # type: ignore[call-overload]
        notification=notification,
    )

    return SendNotificationResponse(task_id=task.task_id)


class TextNotificationsBulk(BaseModel):
    notifications: list[TextNotification] = []


@router.post(
    '/bulk/text',
    name='notifications:send-text-bulk',
    response_model=SendNotificationResponse,
)
async def send_text_notifications_bulk(notifications: TextNotificationsBulk) -> SendNotificationResponse:
    task: AsyncTaskiqTask[None] = await send_text_notifications_bulk_task.kiq(  # type: ignore[call-overload]
        notifications=notifications.notifications,
    )

    return SendNotificationResponse(task_id=task.task_id)


@router.post(
    '/send/template',
    name='notifications:send-text',
    response_model=SendNotificationResponse,
)
async def send_template_notification(notification: TemplateNotification) -> SendNotificationResponse:
    task: AsyncTaskiqTask[None] = await send_template_notification_task.kiq(  # type: ignore[call-overload]
        notification=notification,
    )

    return SendNotificationResponse(task_id=task.task_id)


class TemplateNotificationsBulk(BaseModel):
    notifications: list[TemplateNotification] = []


@router.post(
    '/bulk/template',
    name='notifications:send-template-bulk',
    response_model=SendNotificationResponse,
)
async def send_template_notifications_bulk(notifications: TemplateNotificationsBulk) -> SendNotificationResponse:
    task: AsyncTaskiqTask[None] = await send_template_notifications_bulk_task.kiq(  # type: ignore[call-overload]
        notifications=notifications.notifications,
    )

    return SendNotificationResponse(task_id=task.task_id)
