from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends

from .models.base import NotificationType
from ..core.config import settings
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
            "template_id": str(settings.templates.registration)
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
            "template_id": str(settings.templates.registration),
            "template_context": {
                "film_id": str(film_id)
            }
        }

        return await self._queue.send(settings.queue.notification_url_template, payload)


async def get_event_service(queue: QueueServiceDep) -> EventService:
    return EventService(queue=queue)

EventServiceDep = Annotated[
    EventService,
    Depends(get_event_service)
]
