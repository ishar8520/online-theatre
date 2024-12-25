from __future__ import annotations

from collections.abc import Callable, Awaitable, AsyncGenerator

import aiohttp
import elasticsearch
import pytest_asyncio
import redis.asyncio as redis

from .data.elasticsearch.schema import indices_data
from .settings import settings
from .utils.elasticsearch import ElasticsearchIndex
from .utils.redis import RedisCache


@pytest_asyncio.fixture(scope='session')
async def aiohttp_session() -> AsyncGenerator[aiohttp.ClientSession]:
    async with aiohttp.ClientSession() as session:
        yield session


@pytest_asyncio.fixture(scope='session')
async def redis_client() -> AsyncGenerator[redis.Redis]:
    async with redis.Redis(host=settings.redis.host, port=settings.redis.port) as redis_client:
        yield redis_client


@pytest_asyncio.fixture
async def redis_cache(
        redis_client: redis.Redis,
) -> AsyncGenerator[RedisCache]:
    redis_cache = RedisCache(client=redis_client)
    await redis_cache.clear()
    yield redis_cache
    await redis_cache.clear()


@pytest_asyncio.fixture
async def clear_redis_cache(
        redis_client: redis.Redis,
) -> AsyncGenerator[Callable[[], Awaitable[None]]]:
    redis_cache = RedisCache(client=redis_client)

    async def _clear_redis_cache() -> None:
        await redis_cache.clear()

    await _clear_redis_cache()
    yield _clear_redis_cache
    await _clear_redis_cache()


@pytest_asyncio.fixture(scope='session')
async def elasticsearch_client() -> AsyncGenerator[elasticsearch.AsyncElasticsearch]:
    async with elasticsearch.AsyncElasticsearch(settings.elasticsearch.url) as elasticsearch_client:
        yield elasticsearch_client


@pytest_asyncio.fixture
async def create_elasticsearch_index(
        elasticsearch_client: elasticsearch.AsyncElasticsearch,
) -> AsyncGenerator[Callable[..., Awaitable[ElasticsearchIndex]]]:
    elasticsearch_indices_registry: dict[str, ElasticsearchIndex] = {}

    async def _create_elasticsearch_index(*, index_name: str) -> ElasticsearchIndex:
        index_data = indices_data.get(index_name)
        if index_data is None:
            raise ValueError('Указан неизвестный индекс Elasticsearch')

        elasticsearch_index = elasticsearch_indices_registry.get(index_name)
        if elasticsearch_index is not None:
            return elasticsearch_index

        elasticsearch_index = ElasticsearchIndex(
            client=elasticsearch_client,
            index_name=index_name,
            index_data=index_data,
        )
        elasticsearch_indices_registry[index_name] = elasticsearch_index
        await elasticsearch_index.create_index(recreate=True)

        return elasticsearch_index

    yield _create_elasticsearch_index

    for _elasticsearch_index in elasticsearch_indices_registry.values():
        await _elasticsearch_index.delete_index()
