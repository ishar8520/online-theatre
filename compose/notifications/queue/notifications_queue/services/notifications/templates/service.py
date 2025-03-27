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
from ...admin_panel import (
    Template,
    AbstractAdminPanelService,
    AdminPanelServiceTaskiqDep,
)

logger = logging.getLogger(__name__)


class AbstractNotificationTemplateService(abc.ABC):
    @abc.abstractmethod
    async def render_text_notification(self, *, notification: TextNotification) -> None: ...

    @abc.abstractmethod
    async def render_template_notification(self, *, notification: TemplateNotification) -> None: ...


class NotificationTemplateService(AbstractNotificationTemplateService):
    admin_panel_service: AbstractAdminPanelService

    def __init__(self, *, admin_panel_service: AbstractAdminPanelService) -> None:
        self.admin_panel_service = admin_panel_service

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

        template = await self._download_template(notification=notification)
        logger.info('template=%r', template)

        message = NotificationMessage(
            type=notification.type,
            subject=notification.subject,
            text='<Rendered message text>',
        )

        await process_notification_users_task.kiq(  # type: ignore[call-overload]
            message=message,
            users=notification.users
        )

    async def _download_template(self, *, notification: TemplateNotification) -> Template | None:
        if notification.template_id is not None:
            template = await self.admin_panel_service.get_template_by_id(
                template_id=notification.template_id,
            )

            if template is not None:
                return template

        if notification.template_code is not None:
            template = await self.admin_panel_service.get_template_by_code(
                template_code=notification.template_code,
            )

            if template is not None:
                return template

        return None


async def get_notification_template_service(
        admin_panel_service: AdminPanelServiceTaskiqDep) -> AbstractNotificationTemplateService:
    return NotificationTemplateService(admin_panel_service=admin_panel_service)


NotificationTemplateServiceTaskiqDep = Annotated[
    AbstractNotificationTemplateService,
    TaskiqDepends(get_notification_template_service),
]
