from __future__ import annotations

from ..broker import broker
from ..services.notifications import (
    TextNotification,
    TemplateNotification,
    NotificationsServiceTaskiqDep,
)


@broker.task
async def send_text_notification_task(*,
                                      notification: TextNotification,
                                      notification_service: NotificationsServiceTaskiqDep) -> None:
    await notification_service.send_text_notification(notification=notification)


@broker.task
async def send_text_notifications_bulk_task(*,
                                            notifications: list[TextNotification],
                                            notification_service: NotificationsServiceTaskiqDep) -> None:
    await notification_service.send_text_notifications_bulk(notifications=notifications)


@broker.task
async def send_template_notification_task(*,
                                          notification: TemplateNotification,
                                          notification_service: NotificationsServiceTaskiqDep) -> None:
    await notification_service.send_template_notification(notification=notification)


@broker.task
async def send_template_notifications_bulk_task(*,
                                                notifications: list[TemplateNotification],
                                                notification_service: NotificationsServiceTaskiqDep) -> None:
    await notification_service.send_template_notifications_bulk(notifications=notifications)
