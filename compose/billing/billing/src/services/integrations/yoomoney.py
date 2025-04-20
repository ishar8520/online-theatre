from __future__ import annotations

import logging
from http import HTTPStatus

import aiohttp

from src.core.config import settings
from src.models.sqlalchemy import Payment
from src.services.integrations.abstract import AbstractIntegration
from src.services.integrations.exceptions import IntegrationCreatePaymentError


class YoomoneyService(AbstractIntegration):
    """
    Integration service for YooMoney payment provider.

    Implements payment creation and refund operations via YooMoney API.
    """

    async def create(self, payment: Payment) -> str:
        """
        Create a payment in YooMoney and return the accept URL.

        :param payment: Payment object from the billing service
        :return: URL for user redirection to approve the payment
        :raise IntegrationCreatePaymentError: if the creation request fails
        """
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
                        data = await response.json()  # type: dict[str, str]
                        return data["accept_url"]

                    logging.debug(f"Yoomoney.create: status=:{response.status}, response={response}")
                    raise IntegrationCreatePaymentError

        except Exception as err:
            logging.debug(f"Yoomoney.create: error:{err}")
            raise IntegrationCreatePaymentError

    async def refund(self, payment: Payment) -> str:
        """
        Initiate a refund in YooMoney and return the refund URL.

        :param payment: Payment object from the billing service
        :return: URL for user redirection to complete the refund
        :raise IntegrationCreatePaymentError: if the refund request fails
        """
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
                        data = await response.json()  # type: dict[str, str]
                        return data["accept_url"]

                    logging.debug(f"Yoomoney.refund: status=:{response.status}, response={response}")
                    raise IntegrationCreatePaymentError

        except Exception as err:
            logging.debug(f"Yoomoney.refund: error:{err}")
            raise IntegrationCreatePaymentError

    @staticmethod
    def get_url() -> str:
        """
        Get the base URL for YooMoney integration endpoints.

        :return: Base URL string constructed from service settings
        """
        return f"{settings.payment_service.base_url}/yoomoney"
