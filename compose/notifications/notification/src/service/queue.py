from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Annotated

import aiohttp
from fastapi import Depends

from .exceptions.queue import QueueSendException


logging.basicConfig(level=logging.INFO)


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
                    if response.status == HTTPStatus.OK:
                        return True

                    data = await response.json()
                    logging.debug(f'QueueService.send: status=:{response.status}, data={data}')

                    return False

        except Exception as err:
            logging.debug(f'QueueService.send: error:{err}')
            raise QueueSendException


async def get_queue_service() -> QueueService:
    return QueueService()

QueueServiceDep = Annotated[
    QueueService,
    Depends(get_queue_service)
]
