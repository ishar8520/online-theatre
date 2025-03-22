from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from .models.message import (
    PersonalizedMessageDto,
    BroadcastMessageDto
)
from ..service.queue import (
    QueueService,
    QueueServiceDep
)


class MessageService:
    _queue: QueueService

    def __init__(self, queue: QueueService):
        self._queue = queue

    async def send_personalized(self, message: PersonalizedMessageDto) -> bool:
        return await self._queue.send(message.model_dump())

    async def send_broadcast(self, message: BroadcastMessageDto) -> bool:
        return await self._queue.send(message.model_dump())

async def get_message_service(queue: QueueServiceDep) -> MessageService:
    return MessageService(queue=queue)

MessageServiceDep = Annotated[
    MessageService,
    Depends(get_message_service)
]


