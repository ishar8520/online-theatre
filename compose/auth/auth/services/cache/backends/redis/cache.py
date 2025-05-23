from __future__ import annotations

from typing import Any

import backoff
import redis.asyncio as async_redis
import redis.exceptions

from ..base import BaseCache


class RedisCache(BaseCache):
    redis_client: async_redis.Redis

    def __init__(self, *, redis_client: async_redis.Redis, **kwargs: Any) -> None:
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
    async def _set_value(self, key: str, value: str, *, timeout: int | None) -> None:
        await self.redis_client.set(key, value, ex=timeout)

    @backoff.on_exception(backoff.expo, (
            redis.exceptions.ConnectionError,
            redis.exceptions.TimeoutError,
    ))
    async def _delete_key(self, key: str) -> None:
        await self.redis_client.delete(key)
