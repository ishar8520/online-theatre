from __future__ import annotations

import uuid
from typing import Annotated

import aiohttp
from fastapi import Depends

from ..core.config import settings


class QueueService:
    _session: aiohttp.ClientSession

    def __init__(self):
        self._queue_url = settings.queue.queue_url

    async def send(self, payload: dict) -> dict:
        data = await self._process_before_request(payload)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self._queue_url,
                json=data
            ) as response:
                data_json = await response.json()

                return data_json

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
