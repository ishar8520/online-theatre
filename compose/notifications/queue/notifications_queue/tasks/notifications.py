from __future__ import annotations

from ..broker import broker
from ..services.notifications import (
    Notification,
    NotificationsServiceTaskiqDep,
)


@broker.task
async def send_notification_task(*,
                                 notification: Notification,
                                 notification_service: NotificationsServiceTaskiqDep) -> None:
    await notification_service.send_notification(notification=notification)
