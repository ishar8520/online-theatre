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
        payload = {
            "amount": payment.price,
            "label": str(payment.id),
            "message": f"Order for user {payment.user_id}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"{base_url}/payment/{payment.user_id}",
                    json=payload
                ) as response:
                    if response.status == HTTPStatus.OK:
                        data = await response.json()
                        return data["accept_url"]

                    logging.debug(f"Yoomoney.create: status=:{response.status}, response={response}")
                    raise IntegrationCreatePaymentError

        except Exception as err:
            logging.debug(f"Yoomoney.create: error:{err}")
            raise IntegrationCreatePaymentError

    async def refund(self, payment: Payment) -> str:
        base_url = self.get_url()
        payload = {
            "amount": payment.price,
            "label": str(payment.id),
            "message": f"Refund for user {payment.user_id}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"{base_url}/refund/{payment.user_id}",
                    json=payload
                ) as response:
                    if response.status == HTTPStatus.OK:
                        data = await response.json()
                        return data["accept_url"]

                    logging.debug(f"Yoomoney.refund: status=:{response.status}, response={response}")
                    raise IntegrationCreatePaymentError

        except Exception as err:
            logging.debug(f"Yoomoney.refund: error:{err}")
            raise IntegrationCreatePaymentError

    @staticmethod
    def get_url():
        return f"{settings.payment_service.base_url}/yoomoney"

