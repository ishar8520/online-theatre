from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from src.core.config import settings
from src.services.integrations.abstract import AbstractIntegration, AbstractIntegrationFactory
from src.services.integrations.exceptions import UnsupportedIntegrationTypeError
from src.services.integrations.models import PaymentIntegrations
from src.services.integrations.yoomoney import YoomoneyService
from src.tests.integration import TestIntegrationFactory


class IntegrationFactory(AbstractIntegrationFactory):
    """
    Concrete factory for payment provider integrations.

    Provides the appropriate AbstractIntegration implementation
    based on the requested provider type.
    """

    @staticmethod
    async def get(integration: PaymentIntegrations) -> AbstractIntegration:
        """
        Return an integration instance for the specified provider.

        :param integration: Member of the PaymentIntegrations enum
                            indicating which provider to use.
        :return: Instance implementing AbstractIntegration.
        :raises UnsupportedIntegrationTypeError: If the integration type is not supported.
        """
        if integration == PaymentIntegrations.YOOMONEY:
            return YoomoneyService()

        raise UnsupportedIntegrationTypeError


def get_integration_factory() -> AbstractIntegrationFactory:
    """
    Return the active integration factory based on application mode.

    :return: TestIntegrationFactory if test_mode is enabled; otherwise IntegrationFactory.
    """
    if settings.test_mode:
        return TestIntegrationFactory()

    return IntegrationFactory()


IntegrationFactoryDep = Annotated[
    IntegrationFactory,
    Depends(get_integration_factory)
]
