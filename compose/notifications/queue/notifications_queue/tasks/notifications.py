from __future__ import annotations

import datetime
import uuid

from ..broker import (
    broker,
    undelivered_messages_broker,
)
from ..services.auth import (
    User,
)
from ..services.notifications import (
    TextNotification,
    TemplateNotification,
    NotificationMessage,
    NotificationServiceTaskiqDep,
    NotificationTemplateServiceTaskiqDep,
    NotificationUserServiceTaskiqDep,
    NotificationMessageServiceTaskiqDep,
)


@broker.task
async def send_text_notification_task(*,
                                      notification: TextNotification,
                                      notification_service: NotificationServiceTaskiqDep) -> None:
    await notification_service.send_text_notification(notification=notification)


@broker.task
async def send_template_notification_task(*,
                                          notification: TemplateNotification,
                                          notification_service: NotificationServiceTaskiqDep) -> None:
    await notification_service.send_template_notification(notification=notification)


@broker.task
async def send_text_notifications_bulk_task(*,
                                            notifications: list[TextNotification],
                                            notification_service: NotificationServiceTaskiqDep) -> None:
    await notification_service.send_text_notifications_bulk(notifications=notifications)


@broker.task
async def send_template_notifications_bulk_task(*,
                                                notifications: list[TemplateNotification],
                                                notification_service: NotificationServiceTaskiqDep) -> None:
    await notification_service.send_template_notifications_bulk(notifications=notifications)


@broker.task
async def render_text_notification_task(
        *,
        notification: TextNotification,
        notification_template_service: NotificationTemplateServiceTaskiqDep) -> None:
    await notification_template_service.render_text_notification(notification=notification)


@broker.task
async def render_template_notification_task(
        *,
        notification: TemplateNotification,
        notification_template_service: NotificationTemplateServiceTaskiqDep) -> None:
    await notification_template_service.render_template_notification(notification=notification)


@broker.task
async def process_notification_users_task(
        *,
        message: NotificationMessage,
        users: list[uuid.UUID],
        notification_user_service: NotificationUserServiceTaskiqDep) -> None:
    await notification_user_service.process_notification_users(
        message=message,
        users=users,
    )


@broker.task
async def download_selected_users_task(
        *,
        message: NotificationMessage,
        users: list[uuid.UUID],
        notification_user_service: NotificationUserServiceTaskiqDep) -> None:
    await notification_user_service.download_selected_users(
        message=message,
        users=users,
    )


@broker.task
async def download_user_task(
        *,
        message: NotificationMessage,
        user_id: uuid.UUID,
        notification_user_service: NotificationUserServiceTaskiqDep) -> None:
    await notification_user_service.download_user(
        message=message,
        user_id=user_id,
    )


@broker.task
async def download_all_users_task(
        *,
        message: NotificationMessage,
        user_id: uuid.UUID | None = None,
        user_created: datetime.datetime | None = None,
        notification_user_service: NotificationUserServiceTaskiqDep) -> None:
    await notification_user_service.download_all_users(
        message=message,
        user_id=user_id,
        user_created=user_created,
    )


@broker.task
async def process_notification_message_task(
        *,
        message: NotificationMessage,
        user: User,
        notification_message_service: NotificationMessageServiceTaskiqDep) -> None:
    await notification_message_service.process_notification_message(
        message=message,
        user=user,
    )


@broker.task
async def send_email_message_task(
        *,
        email: str,
        subject: str,
        text: str,
        notification_message_service: NotificationMessageServiceTaskiqDep) -> None:
    await notification_message_service.send_email_message(
        email=email,
        subject=subject,
        text=text,
    )


@undelivered_messages_broker.task
async def send_email_message_retry_task(
        *,
        email: str,
        subject: str,
        text: str,
        notification_message_service: NotificationMessageServiceTaskiqDep) -> None:
    await notification_message_service.send_email_message_retry(
        email=email,
        subject=subject,
        text=text,
    )
