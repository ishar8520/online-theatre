from __future__ import annotations

import abc
from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends

from .cache import (
    AbstractCache,
    RedisCache,
)
from ...db import RedisClientDep


class AbstractCacheService(abc.ABC):
    @abc.abstractmethod
    def get_cache(self,
                  *,
                  key_prefix: str | None = None,
                  key_version: str | None = None) -> AbstractCache: ...


class RedisCacheService(AbstractCacheService):
    redis_client: redis.Redis

    def __init__(self, *, redis_client: redis.Redis) -> None:
        self.redis_client = redis_client

    def get_cache(self,
                  *,
                  key_prefix: str | None = None,
                  key_version: str | None = None) -> RedisCache:
        return RedisCache(
            redis_client=self.redis_client,
            key_prefix=key_prefix,
            key_version=key_version,
        )


async def get_cache_service(redis_client: RedisClientDep) -> AbstractCacheService:
    return RedisCacheService(redis_client=redis_client)


CacheServiceDep = Annotated[AbstractCacheService, Depends(get_cache_service)]
