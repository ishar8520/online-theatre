import aio_pika
from aio_pika.abc import AbstractRobustConnection

from payment.core.config import settings


class RabbitMQ:
    """Сервис для работы с подключением к RabbitMQ."""

    def __init__(self):
        """Инициализирует экземпляр класса RabbitMQ."""
        self.connection: AbstractRobustConnection | None = None
        self.channel = None

    async def connect(self):
        """
        Устанавливает соединение с RabbitMQ и открывает канал.

        :return: Экземпляр класса RabbitMQ с активным соединением
        """
        self.connection = await aio_pika.connect_robust(settings.rabbitmq.url)
        self.channel = await self.connection.channel()
        return self

    async def close(self):
        """Закрывает соединение с RabbitMQ, если оно было открыто."""
        if self.connection:
            await self.connection.close()


rabbitmq = RabbitMQ()
