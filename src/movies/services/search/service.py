from __future__ import annotations

from typing import Annotated

import backoff
import elasticsearch
from fastapi import Depends

from .cache import SearchCache
from ..cache import (
    AbstractCacheService,
    CacheServiceDep,
)
from ...db import ElasticsearchClientDep


class SearchService:
    elasticsearch_client: elasticsearch.AsyncElasticsearch
    search_cache: SearchCache

    def __init__(self,
                 *,
                 elasticsearch_client: elasticsearch.AsyncElasticsearch,
                 cache_service: AbstractCacheService) -> None:
        self.elasticsearch_client = elasticsearch_client
        cache = cache_service.get_cache(key_prefix='search')
        self.search_cache = SearchCache(cache=cache)

    @backoff.on_exception(backoff.expo, (
            elasticsearch.exceptions.ConnectionError,
            elasticsearch.exceptions.ConnectionTimeout,
    ))
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

    @backoff.on_exception(backoff.expo, (
            elasticsearch.exceptions.ConnectionError,
            elasticsearch.exceptions.ConnectionTimeout,
    ))
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


async def get_search_service(elasticsearch_client: ElasticsearchClientDep,
                             cache_service: CacheServiceDep) -> SearchService:
    return SearchService(
        elasticsearch_client=elasticsearch_client,
        cache_service=cache_service,
    )


SearchServiceDep = Annotated[SearchService, Depends(get_search_service)]
