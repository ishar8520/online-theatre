from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends

from .models.base import NotificationType
from ..core.config import settings
from ..core.templates import TemplateList
from ..service.queue import (
    QueueService,
    QueueServiceDep
)


class EventService:
    _queue: QueueService

    def __init__(self, queue: QueueService):
        self._queue = queue

    async def on_user_registration(
            self,
            user_id: uuid.UUID,
            notification_type: NotificationType
    ) -> bool:

        payload = {
            "users": [str(user_id)],
            "subject": "Registration",
            "type": notification_type,
            "template_code": TemplateList.REGISTRATION,
        }

        return await self._queue.send(settings.queue.notification_url_template, payload)

    async def on_add_new_movie(
            self,
            film_id: uuid.UUID,
            notification_type: NotificationType
    ) -> bool:

        payload = {
            "subject": "New movie",
            "type": notification_type,
            "template_code": TemplateList.ON_NEW_MOVIE,
            "template_context": {
                "film_id": str(film_id)
            }
        }

        return await self._queue.send(settings.queue.notification_url_template, payload)

    async def on_payment_status(
        self,
        user_id: uuid.UUID,
        payment_status: str,
        notification_type: NotificationType
    ) -> bool:
        if payment_status == 'success':
            payment_status = 'прошел успешно'
        elif payment_status == 'failed':
            payment_status = 'завершился с ошибкой'
        
        payload = {
            "users": [str(user_id)],
            "subject": "Payment status",
            "type": notification_type,
            "template_code": TemplateList.PAYMENT_STATUS,
            "template_context": {
                "payment_status": payment_status
            }
        }
        
        return await self._queue.send(settings.queue.notification_url_template, payload)


async def get_event_service(queue: QueueServiceDep) -> EventService:
    return EventService(queue=queue)

EventServiceDep = Annotated[
    EventService,
    Depends(get_event_service)
]
