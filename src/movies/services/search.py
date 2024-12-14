from __future__ import annotations

import hashlib
import json
from typing import Any

import elasticsearch
import redis.asyncio as redis

from ..core import config


class SearchService:
    elasticsearch_client: elasticsearch.AsyncElasticsearch
    search_cache: SearchCache

    def __init__(self,
                 *,
                 elasticsearch_client: elasticsearch.AsyncElasticsearch,
                 redis_client: redis.Redis) -> None:
        self.elasticsearch_client = elasticsearch_client
        self.search_cache = SearchCache(redis_client=redis_client)

    async def get(self, *, index: str, id: str) -> dict | None:
        search_params = {
            'id': id,
        }
        result = await self.search_cache.get(index=index, command='get', params=search_params)

        if result is not None:
            return result

        try:
            response = await self.elasticsearch_client.get(index=index, id=id)
        except elasticsearch.NotFoundError:
            return None

        result = response['_source']
        await self.search_cache.set(index=index, command='get', params=search_params, value=result)

        return result

    async def search(self, *, index: str, body: dict) -> list[dict] | None:
        search_params = {
            'body': body,
        }
        result = await self.search_cache.get(index=index, command='search', params=search_params)

        if result is not None:
            return result

        try:
            response = await self.elasticsearch_client.search(index=index, body=body)
        except elasticsearch.NotFoundError:
            return None

        result = response['hits']['hits']

        if not result:
            return None

        await self.search_cache.set(index=index, command='search', params=search_params, value=result)

        return result


class SearchCache:
    redis_client: redis.Redis
    key_version: str

    def __init__(self,
                 *,
                 redis_client: redis.Redis,
                 key_version: str | None = None) -> None:
        self.redis_client = redis_client
        self.key_version = key_version or '1.0'

    async def get(self, *, index: str, command: str, params: dict) -> Any | None:
        cache_key = self._create_cache_key(index=index, command=command, params=params)
        value_json: str | None = await self.redis_client.get(cache_key)

        if value_json is None:
            return None

        return json.loads(value_json)

    async def set(self, *, index: str, command: str, params: dict, value: Any) -> None:
        cache_key = self._create_cache_key(index=index, command=command, params=params)
        value_json = json.dumps(value)

        await self.redis_client.set(
            cache_key,
            value_json,
            ex=config.REDIS_CACHE_EXPIRE_IN_SECONDS,
        )

    def _create_cache_key(self, *, index: str, command: str, params: dict) -> str:
        key_dict = {
            'version': self.key_version,
            'index': index,
            'command': command,
            'params': params,
        }
        key_json = json.dumps(key_dict, sort_keys=True)
        key_hash = hashlib.sha256(key_json.encode()).hexdigest()

        return f'search-{index}-{command}-{key_hash}'
