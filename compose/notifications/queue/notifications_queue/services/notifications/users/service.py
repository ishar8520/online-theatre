from __future__ import annotations

import abc
import datetime
import logging
import uuid
from typing import Annotated

from taskiq import TaskiqDepends

from ..models import NotificationMessage
from ...auth import (
    AbstractAuthService,
    AuthServiceTaskiqDep,
)

logger = logging.getLogger(__name__)


class AbstractNotificationUserService(abc.ABC):
    @abc.abstractmethod
    async def process_notification_users(self,
                                         *,
                                         message: NotificationMessage,
                                         users: list[uuid.UUID]) -> None: ...

    @abc.abstractmethod
    async def download_selected_users(self,
                                      *,
                                      message: NotificationMessage,
                                      users: list[uuid.UUID]) -> None: ...

    @abc.abstractmethod
    async def download_user(self,
                            *,
                            message: NotificationMessage,
                            user_id: uuid.UUID) -> None: ...

    @abc.abstractmethod
    async def download_all_users(self,
                                 *,
                                 message: NotificationMessage,
                                 user_id: uuid.UUID | None = None,
                                 user_created: datetime.datetime | None = None) -> None: ...


class NotificationUserService(AbstractNotificationUserService):
    auth_service: AbstractAuthService

    def __init__(self, *, auth_service: AbstractAuthService) -> None:
        self.auth_service = auth_service

    async def process_notification_users(self,
                                         *,
                                         message: NotificationMessage,
                                         users: list[uuid.UUID]) -> None:
        from ....tasks import (
            download_selected_users_task,
            download_all_users_task,
        )

        logger.info('NotificationUserService.process_notification_users()')
        logger.info('message=%r', message)
        logger.info('users=%r', users)

        if users:
            await download_selected_users_task.kiq(  # type: ignore[call-overload]
                message=message,
                users=users,
            )
        else:
            await download_all_users_task.kiq(  # type: ignore[call-overload]
                message=message,
            )

    async def download_selected_users(self,
                                      *,
                                      message: NotificationMessage,
                                      users: list[uuid.UUID]) -> None:
        from ....tasks import download_user_task

        logger.info('NotificationUserService.download_selected_users()')
        logger.info('message=%r', message)
        logger.info('users=%r', users)

        for user_id in users:
            await download_user_task.kiq(  # type: ignore[call-overload]
                message=message,
                user_id=user_id,
            )

    async def download_user(self,
                            *,
                            message: NotificationMessage,
                            user_id: uuid.UUID) -> None:
        from ....tasks import process_notification_message_task

        logger.info('NotificationUserService.download_user()')
        logger.info('message=%r', message)
        logger.info('user_id=%r', user_id)

        user = await self.auth_service.get_user(user_id=user_id)
        logger.info('user=%r', user)

        if user is None:
            return

        await process_notification_message_task.kiq(  # type: ignore[call-overload]
            message=message,
            user=user,
        )

    async def download_all_users(self,
                                 *,
                                 message: NotificationMessage,
                                 user_id: uuid.UUID | None = None,
                                 user_created: datetime.datetime | None = None) -> None:
        from ....tasks import (
            download_all_users_task,
            process_notification_message_task,
        )

        logger.info('NotificationUserService.download_all_users()')
        logger.info('message=%r', message)
        logger.info('user_id=%r', user_id)
        logger.info('user_created=%r', user_created)

        users_list = await self.auth_service.get_users_list(
            user_id=user_id,
            user_created=user_created,
        )
        logger.info('users_list=%r', users_list)

        if not users_list:
            return

        for user in users_list:
            logger.info('user=%r', user)

            await process_notification_message_task.kiq(  # type: ignore[call-overload]
                message=message,
                user=user,
            )

        await download_all_users_task.kiq(  # type: ignore[call-overload]
            message=message,
            user_id=users_list[-1].id,
            user_created=users_list[-1].created,
        )


async def get_notification_user_service(auth_service: AuthServiceTaskiqDep) -> AbstractNotificationUserService:
    return NotificationUserService(auth_service=auth_service)


NotificationUserServiceTaskiqDep = Annotated[
    AbstractNotificationUserService,
    TaskiqDepends(get_notification_user_service),
]
