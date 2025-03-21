from __future__ import annotations

import abc
import logging
import uuid
from collections.abc import Iterable
from typing import Annotated

from taskiq import TaskiqDepends

from .models import (
    NotificationType,
    TextNotification,
    TemplateNotification,
)
from ..auth import (
    AbstractAuthService,
    AuthServiceTaskiqDep,
    User,
)

logger = logging.getLogger(__name__)


class AbstractNotificationsService(abc.ABC):
    @abc.abstractmethod
    async def send_text_notification(self, *, notification: TextNotification) -> None: ...

    @abc.abstractmethod
    async def send_text_notifications_bulk(self, *, notifications: Iterable[TextNotification]) -> None: ...

    @abc.abstractmethod
    async def send_template_notification(self, *, notification: TemplateNotification) -> None: ...

    @abc.abstractmethod
    async def send_template_notifications_bulk(self, *, notifications: Iterable[TemplateNotification]) -> None: ...


class NotificationsService(AbstractNotificationsService):
    auth_service: AbstractAuthService

    def __init__(self, *, auth_service: AbstractAuthService) -> None:
        self.auth_service = auth_service

    async def send_text_notification(self, *, notification: TextNotification) -> None:
        logger.info('NotificationsService.send_text_notification()')
        logger.info('notification=%r', notification)

        await self._send_notification(
            notification_type=notification.type,
            users=notification.users,
            subject=notification.subject,
            text=notification.text,
        )

    async def send_text_notifications_bulk(self, *, notifications: Iterable[TextNotification]) -> None:
        logger.info('NotificationsService.send_text_notifications_bulk()')

        for notification in notifications:
            await self.send_text_notification(notification=notification)

    async def send_template_notification(self, *, notification: TemplateNotification) -> None:
        logger.info('NotificationsService.send_template_notification()')
        logger.info('notification=%r', notification)

    async def send_template_notifications_bulk(self, *, notifications: Iterable[TemplateNotification]) -> None:
        logger.info('NotificationsService.send_template_notifications_bulk()')

        for notification in notifications:
            await self.send_template_notification(notification=notification)

    async def _send_notification(self,
                                 *,
                                 notification_type: NotificationType,
                                 users: Iterable[uuid.UUID] | None,
                                 subject: str,
                                 text: str) -> None:
        logger.info('NotificationsService._send_notification()')

        if users is None:
            return

        for user_id in users:
            user = await self.auth_service.get_user(user_id=user_id)
            logger.info('user=%r', user)

            if user is None:
                continue

            if notification_type == NotificationType.EMAIL:
                await self._send_email_message(
                    user=user,
                    subject=subject,
                    text=text,
                )

    async def _send_email_message(self,
                                  *,
                                  user: User,
                                  subject: str,
                                  text: str) -> None:
        pass


async def get_notifications_service(auth_service: AuthServiceTaskiqDep) -> AbstractNotificationsService:
    return NotificationsService(auth_service=auth_service)


NotificationsServiceTaskiqDep = Annotated[
    AbstractNotificationsService,
    TaskiqDepends(get_notifications_service),
]
