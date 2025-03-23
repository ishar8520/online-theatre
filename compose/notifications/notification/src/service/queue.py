from __future__ import annotations

from http import HTTPStatus
from typing import Annotated

import aiohttp
from fastapi import Depends

from .exceptions.queue import QueueSendException


class QueueService:
    async def send(
            self,
            notification_url: str,
            payload: dict
    ) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=notification_url,
                    json=payload
                ) as response:
                    return response.status == HTTPStatus.OK
        except Exception:
            raise QueueSendException


async def get_queue_service() -> QueueService:
    return QueueService()

QueueServiceDep = Annotated[
    QueueService,
    Depends(get_queue_service)
]
