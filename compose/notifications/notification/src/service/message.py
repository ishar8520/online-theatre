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


class MessageService:
    _queue: QueueService

    def __init__(self, queue: QueueService):
        self._queue = queue

    async def send_personalized(
            self,
            user_id: uuid.UUID,
            subject : str,
            template_id : uuid.UUID,
            notification_type : NotificationType,
    ) -> bool:
        payload = {
            "users": [str(user_id)],
            "subject": subject,
            "template_id": str(template_id),
            "type": notification_type
        }

        return await self._queue.send(
            settings.queue.notification_url_template,
            payload
        )

    async def send_broadcast(
            self,
            subject : str,
            template_id : uuid.UUID,
            notification_type : NotificationType,
    ) -> bool:
        payload = {
            "subject": subject,
            "template_id": str(template_id),
            "type": notification_type
        }

        return await self._queue.send(
            settings.queue.notification_url_template,
            payload
        )

async def get_message_service(queue: QueueServiceDep) -> MessageService:
    return MessageService(queue=queue)

MessageServiceDep = Annotated[
    MessageService,
    Depends(get_message_service)
]


