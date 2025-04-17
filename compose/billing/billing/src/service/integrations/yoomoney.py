from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Annotated

import aiohttp
from fastapi import Depends

from .abstract import AbstractIntegration
from .exceptions import IntegrationCreatePaymentError
from ...core.config import settings
from ...models.sqlalchemy import Payment


class YoomoneyService(AbstractIntegration):
    async def create(self, payment: Payment) -> str:
        base_url = self.get_url()
        payload = {}  # @todo use Payment object

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"{base_url}/create",
                    json=payload
                ) as response:
                    if response.status == HTTPStatus.OK:
                        data = await response.json()
                        return data["url"]

                    logging.debug(f"Yoomoney.create: status=:{response.status}, response={response}")
                    raise IntegrationCreatePaymentError

        except Exception as err:
            logging.debug(f"Yoomoney.create: error:{err}")
            raise IntegrationCreatePaymentError

    @staticmethod
    def get_url():
        return f"{settings.payment_service.base_url}/yoomoney"


def get_yoomoney_service():
    return YoomoneyService()


YoomoneyServiceDep = Annotated[YoomoneyService, Depends(get_yoomoney_service)]
