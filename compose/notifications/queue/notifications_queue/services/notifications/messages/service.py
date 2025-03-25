from __future__ import annotations

import abc
import logging
from typing import Annotated

from taskiq import TaskiqDepends

from ..models import (
    NotificationType,
    NotificationMessage,
)
from ...auth import User

logger = logging.getLogger(__name__)


class AbstractNotificationMessageService(abc.ABC):
    @abc.abstractmethod
    async def process_notification_message(self, *, message: NotificationMessage, user: User) -> None: ...

    @abc.abstractmethod
    async def send_email_message(self, *, email: str, subject: str, text: str) -> None: ...


class NotificationMessageService(AbstractNotificationMessageService):
    async def process_notification_message(self, *, message: NotificationMessage, user: User) -> None:
        from ....tasks import send_email_message_task

        logger.info('NotificationMessageService.process_notification_message()')
        logger.info('message=%r', message)
        logger.info('user=%r', user)

        if message.type == NotificationType.EMAIL:
            await send_email_message_task.kiq(  # type: ignore[call-overload]
                email=user.email,
                subject=message.subject,
                text=message.text,
            )

    async def send_email_message(self, *, email: str, subject: str, text: str) -> None:
        logger.info('NotificationMessageService.send_email_message()')
        logger.info('email=%r', email)
        logger.info('subject=%r', subject)
        logger.info('text=%r', text)


async def get_notification_message_service() -> AbstractNotificationMessageService:
    return NotificationMessageService()


NotificationMessageServiceTaskiqDep = Annotated[
    AbstractNotificationMessageService,
    TaskiqDepends(get_notification_message_service),
]
