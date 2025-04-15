import aio_pika
from aio_pika.abc import AbstractRobustConnection

from payment.core.config import settings

class RabbitMQ:
    def __init__(self):
        self.connection: AbstractRobustConnection | None = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(settings.rabbitmq.url)
        self.channel = await self.connection.channel()
        return self

    async def close(self):
        if self.connection:
            await self.connection.close()

rabbitmq = RabbitMQ()
