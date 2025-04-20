from __future__ import annotations

from ..models.sqlalchemy import Payment
from ..services.integrations.abstract import AbstractIntegration, AbstractIntegrationFactory
from ..services.integrations.models import PaymentIntegrations


class TestIntegrationFactory(AbstractIntegrationFactory):
    @staticmethod
    async def get(integration: PaymentIntegrations) -> AbstractIntegration:
        return DummyService()


class DummyService(AbstractIntegration):
    async def create(self, payment: Payment) -> str:
        return "https://your_link_to_pay"

    async def refund(self, payment: Payment) -> str:
        return "https://your_link_to_refund"
