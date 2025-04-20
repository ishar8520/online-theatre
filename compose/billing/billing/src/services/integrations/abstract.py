from abc import ABC, abstractmethod

from src.models.sqlalchemy import Payment
from src.services.integrations.models import PaymentIntegrations


class AbstractIntegration(ABC):
    """
    Base abstract class for payment provider integrations.

    Defines the interface for creating payments and issuing refunds.
    """

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


class AbstractIntegrationFactory(ABC):
    """
    Abstract factory for obtaining payment integration instances.

    Provides a method to retrieve the appropriate integration
    implementation based on the specified provider.
    """

    @staticmethod
    @abstractmethod
    async def get(integration: PaymentIntegrations) -> AbstractIntegration:
        """
        Return an integration instance for the given provider.

        :param integration: Member of the PaymentIntegrations enum
        :return: Instance implementing AbstractIntegration
        """
        pass
