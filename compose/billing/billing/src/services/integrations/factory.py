from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from .abstract import (
    AbstractIntegration,
    AbstractIntegrationFactory
)
from .exceptions import UnsupportedIntegrationType
from .models import PaymentIntegrations
from .yoomoney import YoomoneyService
from ...core.config import settings
from ...tests.integration import TestIntegrationFactory


class IntegrationFactory(AbstractIntegrationFactory):
    @staticmethod
    async def get(integration: PaymentIntegrations) -> AbstractIntegration:
        if integration == PaymentIntegrations.YOOMONEY:
            return YoomoneyService()

        raise UnsupportedIntegrationType


def get_integration_factory():
    if settings.test_mode:
        return TestIntegrationFactory()

    return IntegrationFactory()


IntegrationFactoryDep = Annotated[
    IntegrationFactory,
    Depends(get_integration_factory)
]
