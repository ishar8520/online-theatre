from __future__ import annotations

import abc
from typing import Any

import backoff
import redis.asyncio as redis
import redis.exceptions

from ...core.config import settings


class AbstractCache(abc.ABC):
    @abc.abstractmethod
    async def get(self, key: str) -> str | None: ...

    @abc.abstractmethod
    async def set(self, key: str, value: str) -> None: ...


class BaseCache(AbstractCache):
    key_prefix: str
    key_version: str

    def __init__(self,
                 *,
                 key_prefix: str | None = None,
                 key_version: str | None = None) -> None:
        self.key_prefix = key_prefix or 'cache'
        self.key_version = key_version or '1.0'

    async def get(self, key: str) -> str | None:
        cache_key = self._create_cache_key(key)
        return await self._get_value(cache_key)

    @abc.abstractmethod
    async def _get_value(self, key: str) -> str | None: ...

    async def set(self, key: str, value: str) -> None:
        cache_key = self._create_cache_key(key)
        await self._set_value(cache_key, value)

    @abc.abstractmethod
    async def _set_value(self, key: str, value: str) -> None: ...

    def _create_cache_key(self, key: str) -> str:
        return f'{self.key_prefix}:{self.key_version}:{key}'


class RedisCache(BaseCache):
    redis_client: redis.Redis

    def __init__(self, *, redis_client: redis.Redis, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.redis_client = redis_client

    @backoff.on_exception(backoff.expo, (
            redis.exceptions.ConnectionError,
            redis.exceptions.TimeoutError,
    ))
    async def _get_value(self, key: str) -> str | None:
        return await self.redis_client.get(key)

    @backoff.on_exception(backoff.expo, (
            redis.exceptions.ConnectionError,
            redis.exceptions.TimeoutError,
    ))
    async def _set_value(self, key: str, value: str) -> None:
        await self.redis_client.set(key, value, ex=settings.redis.cache_expire_in_seconds)
