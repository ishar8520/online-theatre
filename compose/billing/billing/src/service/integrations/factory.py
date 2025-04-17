from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from .abstract import AbstractIntegration
from .exceptions import UnsupportedIntegrationType
from .models import PaymentIntegrations
from .yoomoney import YoomoneyService


class IntegrationFactory():
    @staticmethod
    async def get(integration: PaymentIntegrations) -> AbstractIntegration:
        if integration == PaymentIntegrations.YOOMONEY:
            return YoomoneyService()

        raise UnsupportedIntegrationType


def get_integration_factory():
    return IntegrationFactory()


IntegrationFactoryDep = Annotated[
    IntegrationFactory,
    Depends(get_integration_factory)
]
