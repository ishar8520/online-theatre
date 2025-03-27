from typing import Optional
from aio_pika import connect
from aio_pika.abc import AbstractConnection, AbstractChannel
from notifications_queue.core.config import settings

class RabbitMQ:
    _connection: Optional[AbstractConnection] = None
    _channel: Optional[AbstractChannel] = None

    @classmethod
    async def get_connection(cls) -> AbstractConnection:
        if cls._connection is None or cls._connection.is_closed:
            cls._connection = await connect(settings.rabbitmq.url)
        return cls._connection

    @classmethod
    async def get_channel(cls) -> AbstractChannel:
        if cls._channel is None or cls._channel.is_closed:
            connection = await cls.get_connection()
            cls._channel = await connection.channel()
        return cls._channel

    @classmethod
    async def close(cls):
        if cls._channel and not cls._channel.is_closed:
            await cls._channel.close()
            cls._channel = None
        if cls._connection and not cls._connection.is_closed:
            await cls._connection.close()
            cls._connection = None
