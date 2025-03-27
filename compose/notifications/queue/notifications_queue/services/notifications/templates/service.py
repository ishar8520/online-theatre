from __future__ import annotations

import abc
import logging
from typing import Annotated

import jinja2
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
    async def process_text_notification(self, *, notification: TextNotification) -> None: ...

    @abc.abstractmethod
    async def process_template_notification(self, *, notification: TemplateNotification) -> None: ...

    @abc.abstractmethod
    async def download_notification_template(self, *, notification: TemplateNotification) -> None: ...

    @abc.abstractmethod
    async def render_notification_template(self,
                                           *,
                                           notification: TemplateNotification,
                                           template: Template) -> None: ...


class NotificationTemplateService(AbstractNotificationTemplateService):
    admin_panel_service: AbstractAdminPanelService

    def __init__(self, *, admin_panel_service: AbstractAdminPanelService) -> None:
        self.admin_panel_service = admin_panel_service

    async def process_text_notification(self, *, notification: TextNotification) -> None:
        from ....tasks import process_notification_users_task

        logger.info('NotificationTemplateService.process_text_notification()')
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

    async def process_template_notification(self, *, notification: TemplateNotification) -> None:
        from ....tasks import download_notification_template_task

        logger.info('NotificationTemplateService.process_template_notification()')
        logger.info('notification=%r', notification)

        await download_notification_template_task.kiq(  # type: ignore[call-overload]
            notification=notification,
        )

    async def download_notification_template(self, *, notification: TemplateNotification) -> None:
        from ....tasks import render_notification_template_task

        logger.info('NotificationTemplateService.download_notification_template()')
        logger.info('notification=%r', notification)

        template = await self._download_template(notification=notification)
        logger.info('template=%r', template)

        if template is None:
            return

        await render_notification_template_task.kiq(  # type: ignore[call-overload]
            notification=notification,
            template=template,
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

    async def render_notification_template(self,
                                           *,
                                           notification: TemplateNotification,
                                           template: Template) -> None:
        from ....tasks import process_notification_users_task

        logger.info('NotificationTemplateService.render_notification_template()')
        logger.info('notification=%r', notification)
        logger.info('template=%r', template)

        message_template = jinja2.Template(template.body, enable_async=True)
        message_text = await message_template.render_async(**notification.template_context)
        message = NotificationMessage(
            type=notification.type,
            subject=notification.subject,
            text=message_text,
        )
        logger.info('message=%r', message)

        await process_notification_users_task.kiq(  # type: ignore[call-overload]
            message=message,
            users=notification.users
        )


async def get_notification_template_service(
        admin_panel_service: AdminPanelServiceTaskiqDep) -> AbstractNotificationTemplateService:
    return NotificationTemplateService(admin_panel_service=admin_panel_service)


NotificationTemplateServiceTaskiqDep = Annotated[
    AbstractNotificationTemplateService,
    TaskiqDepends(get_notification_template_service),
]
