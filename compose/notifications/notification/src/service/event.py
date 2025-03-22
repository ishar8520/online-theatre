from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends

from ..service.queue import (
    QueueService,
    QueueServiceDep
)


class EventService:
    _queue: QueueService

    def __init__(self, queue: QueueService):
        self._queue = queue

    async def on_user_registration(self, user_id: uuid.UUID) -> bool:

        payload = {
            "user_id": user_id,
            "subject": "Registration"
        }

        return await self._queue.send(payload)

    async def on_add_new_movie(self, film_id: uuid.UUID) -> bool:

        payload = {
            "film_id": film_id,
            "subject": "New movie"
        }

        return await self._queue.send(payload)


async def get_event_service(queue: QueueServiceDep) -> EventService:
    return EventService(queue=queue)

EventServiceDep = Annotated[
    EventService,
    Depends(get_event_service)
]
