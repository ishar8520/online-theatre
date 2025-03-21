from __future__ import annotations

import abc
import logging
from typing import Annotated

from taskiq import TaskiqDepends

from .models import Notification
from ..auth import (
    AbstractAuthService,
    AuthServiceTaskiqDep,
)

logger = logging.getLogger(__name__)


class AbstractNotificationsService(abc.ABC):
    @abc.abstractmethod
    async def send_notification(self, *, notification: Notification) -> None: ...


class NotificationsService(AbstractNotificationsService):
    auth_service: AbstractAuthService

    def __init__(self, *, auth_service: AbstractAuthService) -> None:
        self.auth_service = auth_service

    async def send_notification(self, *, notification: Notification) -> None:
        if notification.user_id is None:
            return

        user = await self.auth_service.get_user(user_id=notification.user_id)
        if user is None:
            return

        logger.info(user)


async def get_notifications_service(auth_service: AuthServiceTaskiqDep) -> AbstractNotificationsService:
    return NotificationsService(auth_service=auth_service)


NotificationsServiceTaskiqDep = Annotated[
    AbstractNotificationsService,
    TaskiqDepends(get_notifications_service),
]
