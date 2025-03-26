from __future__ import annotations

import redis.asyncio as async_redis
from admin_panel.core import settings

redis_client = async_redis.Redis(host=settings.redis.host, port=settings.redis.port, db=0)


class RedisClient:
    _client: async_redis.Redis

    def __init__(self, client: async_redis.Redis) -> None:
        self._client = client
    
    async def get_value(self, key: str):
        return await self._client.get(key)
    
    async def set_value(self, key: str, value: str):
        return await self._client.set(key, value)

    async def delete_value(self, key: str):
        return await self._client.delete(key)


async def get_redis_client() -> RedisClient:
    return RedisClient(redis_client)
