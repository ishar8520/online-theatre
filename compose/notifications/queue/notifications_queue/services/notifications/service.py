from __future__ import annotations

import abc
import logging
from typing import Annotated

from taskiq import TaskiqDepends

from .models import (
    TextNotification,
    TemplateNotification,
)

logger = logging.getLogger(__name__)


class AbstractNotificationService(abc.ABC):
    @abc.abstractmethod
    async def send_text_notification(self, *, notification: TextNotification) -> None: ...

    @abc.abstractmethod
    async def send_template_notification(self, *, notification: TemplateNotification) -> None: ...

    @abc.abstractmethod
    async def send_text_notifications_bulk(self, *, notifications: list[TextNotification]) -> None: ...

    @abc.abstractmethod
    async def send_template_notifications_bulk(self, *, notifications: list[TemplateNotification]) -> None: ...


class NotificationService(AbstractNotificationService):
    async def send_text_notification(self, *, notification: TextNotification) -> None:
        from ...tasks import process_text_notification_task

        logger.info('NotificationService.send_text_notification()')
        logger.info('notification=%r', notification)

        await process_text_notification_task.kiq(  # type: ignore[call-overload]
            notification=notification,
        )

    async def send_template_notification(self, *, notification: TemplateNotification) -> None:
        from ...tasks import process_template_notification_task

        logger.info('NotificationService.send_template_notification()')
        logger.info('notification=%r', notification)

        await process_template_notification_task.kiq(  # type: ignore[call-overload]
            notification=notification,
        )

    async def send_text_notifications_bulk(self, *, notifications: list[TextNotification]) -> None:
        logger.info('NotificationService.send_text_notifications_bulk()')

        for notification in notifications:
            await self.send_text_notification(notification=notification)

    async def send_template_notifications_bulk(self, *, notifications: list[TemplateNotification]) -> None:
        logger.info('NotificationService.send_template_notifications_bulk()')

        for notification in notifications:
            await self.send_template_notification(notification=notification)


async def get_notification_service() -> AbstractNotificationService:
    return NotificationService()


NotificationServiceTaskiqDep = Annotated[
    AbstractNotificationService,
    TaskiqDepends(get_notification_service),
]
