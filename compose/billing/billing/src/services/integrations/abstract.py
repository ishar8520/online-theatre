from abc import ABC, abstractmethod

from ...models.sqlalchemy import Payment


class AbstractIntegration(ABC):
    @abstractmethod
    async def create(self, payment: Payment) -> str:
        """
        Create payment and return url for redirect.

        :param payment: object of payment in billing service
        :return str: redirect url
        :raise IntegrationCreatePaymentError: if creation is failed
        """
        pass

    @abstractmethod
    async def refund(self, payment: Payment) -> str:
        """
        Return refund url for redirect.

        :param payment: object of payment in billing service
        :return str: redirect url
        :raise IntegrationCreatePaymentError: if creation is failed
        """
        pass
