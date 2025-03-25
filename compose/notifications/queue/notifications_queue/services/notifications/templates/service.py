from __future__ import annotations

import abc
import logging
from typing import Annotated

from taskiq import TaskiqDepends

from ..models import (
    TextNotification,
    TemplateNotification,
    NotificationMessage,
)

logger = logging.getLogger(__name__)


class AbstractNotificationTemplateService(abc.ABC):
    @abc.abstractmethod
    async def render_text_notification(self, *, notification: TextNotification) -> None: ...

    @abc.abstractmethod
    async def render_template_notification(self, *, notification: TemplateNotification) -> None: ...


class NotificationTemplateService(AbstractNotificationTemplateService):
    async def render_text_notification(self, *, notification: TextNotification) -> None:
        from ....tasks import process_notification_users_task

        logger.info('NotificationTemplateService.render_text_notification()')
        logger.info('notification=%r', notification)

        message = NotificationMessage(
            type=notification.type,
            subject=notification.subject,
            text=notification.text,
        )

        await process_notification_users_task.kiq(  # type: ignore[call-overload]
            message=message,
            users=notification.users,
        )

    async def render_template_notification(self, *, notification: TemplateNotification) -> None:
        from ....tasks import process_notification_users_task

        logger.info('NotificationTemplateService.render_template_notification()')
        logger.info('notification=%r', notification)

        message = NotificationMessage(
            type=notification.type,
            subject=notification.subject,
            text='<Rendered message text>',
        )

        await process_notification_users_task.kiq(  # type: ignore[call-overload]
            message=message,
            users=notification.users
        )


async def get_notification_template_service() -> AbstractNotificationTemplateService:
    return NotificationTemplateService()


NotificationTemplateServiceTaskiqDep = Annotated[
    AbstractNotificationTemplateService,
    TaskiqDepends(get_notification_template_service),
]
