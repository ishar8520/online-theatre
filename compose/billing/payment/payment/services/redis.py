# mypy: disable-error-code=no-any-return
from typing import Any

import redis.asyncio as async_redis

from payment.core.config import settings

redis_client = async_redis.Redis(host=settings.redis.host, port=settings.redis.port, db=0)


class RedisClient:
    """Асинхронный клиент для взаимодействия с Redis."""

    _client: async_redis.Redis

    def __init__(self, client: async_redis.Redis) -> None:
        """Инициализирует экземпляр RedisClient с асинхронным клиентом Redis."""
        self._client = client

    async def get_value(self, key: str) -> Any:
        """
        Получает значение по ключу из Redis.

        :param key: Ключ, по которому необходимо получить значение
        :return: Значение, хранящееся в Redis
        """
        return await self._client.get(key)

    async def set_value(self, key: str, value: str) -> bool:
        """
        Устанавливает значение по ключу в Redis.

        :param key: Ключ для хранения значения
        :param value: Значение, которое нужно сохранить
        :return: Результат выполнения операции (True/False)
        """
        return await self._client.set(key, value)

    async def delete_value(self, key: str) -> int:
        """
        Удаляет значение по ключу из Redis.

        :param key: Ключ, по которому нужно удалить значение
        :return: Количество удалённых ключей
        """
        return await self._client.delete(key)

    async def set_value_with_ttl(self, key: str, value: str, ttl_seconds: int = 600) -> bool:
        """
        Устанавливает значение по ключу в Redis с временем жизни (TTL).

        :param key: Ключ для хранения значения
        :param value: Значение, которое нужно сохранить
        :param ttl_seconds: Время жизни ключа в секундах (по умолчанию 600)
        :return: Результат выполнения операции (True/False)
        """
        return await self._client.setex(key, ttl_seconds, value)


async def get_redis_client() -> RedisClient:
    """
    Функция для получения экземпляра RedisClient с предварительно настроенным подключением.

    :return: Экземпляр RedisClient
    """
    return RedisClient(redis_client)
