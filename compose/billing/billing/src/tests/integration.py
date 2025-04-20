from __future__ import annotations

from src.models.sqlalchemy import Payment
from src.services.integrations.abstract import AbstractIntegration, AbstractIntegrationFactory
from src.services.integrations.models import PaymentIntegrations


class TestIntegrationFactory(AbstractIntegrationFactory):
    """
    Тестовая фабрика интеграций.

    Возвращает DummyService для любых типов интеграций при тестировании.
    """

    @staticmethod
    async def get(integration: PaymentIntegrations) -> AbstractIntegration:
        """
        Возвращает тестовую реализацию интеграции.

        :param integration: запрошенный тип интеграции (игнорируется)
        :return: экземпляр DummyService
        """
        return DummyService()


class DummyService(AbstractIntegration):
    """
    Тестовая реализация абстрактной интеграции.

    Создает фиктивные URL для оплаты и возврата без обращения к реальным API.
    """

    async def create(self, payment: Payment) -> str:
        """
        Возвращает тестовый URL для оплаты.

        :param payment: объект Payment (игнорируется)
        :return: фиксированный URL для перехода на страницу оплаты
        """
        return "https://your_link_to_pay"

    async def refund(self, payment: Payment) -> str:
        """
        Возвращает тестовый URL для возврата.

        :param payment: объект Payment (игнорируется)
        :return: фиксированный URL для перехода на страницу возврата
        """
        return "https://your_link_to_refund"
