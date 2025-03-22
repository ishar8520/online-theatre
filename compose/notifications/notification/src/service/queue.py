from __future__ import annotations

import uuid
from http import HTTPStatus
from typing import Annotated

import aiohttp
from fastapi import Depends

from .exceptions.queue import QueueSendException
from ..core.config import settings


class QueueService:
    _session: aiohttp.ClientSession

    def __init__(self):
        self._queue_url = settings.queue.queue_url

    async def send(self, payload: dict) -> bool:
        data = await self._process_before_request(payload)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=self._queue_url,
                    json=data
                ) as response:
                    return response.status == HTTPStatus.OK
        except Exception:
            raise QueueSendException


    @staticmethod
    async def _process_before_request(payload: dict) -> dict:
        result = {}

        print(payload)

        for key, value in payload.items():
            if isinstance(value, uuid.UUID):
                result[key] = str(value)

            result[key] = str(value)

        return result


async def get_queue_service() -> QueueService:
    return QueueService()

QueueServiceDep = Annotated[
    QueueService,
    Depends(get_queue_service)
]
