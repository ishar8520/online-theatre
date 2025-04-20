import aio_pika
from aio_pika.abc import AbstractChannel, AbstractRobustConnection

from payment.core.config import settings


class RabbitMQ:
    """Сервис для работы с подключением к RabbitMQ."""

    def __init__(self) -> None:
        """Инициализирует экземпляр класса RabbitMQ."""
        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractChannel | None = None

    async def connect(self) -> "RabbitMQ":
        """
        Устанавливает соединение с RabbitMQ и открывает канал.

        :return: Экземпляр класса RabbitMQ с активным соединением
        """
        self.connection = await aio_pika.connect_robust(settings.rabbitmq.url)
        self.channel = await self.connection.channel()
        return self

    async def close(self) -> None:
        """Закрывает соединение с RabbitMQ, если оно было открыто."""
        if self.connection:
            await self.connection.close()


rabbitmq: RabbitMQ = RabbitMQ()
