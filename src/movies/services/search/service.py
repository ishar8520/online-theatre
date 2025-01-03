from __future__ import annotations

import abc
from typing import Annotated

from fastapi import Depends

from .backend import (
    AbstractSearchBackend,
    SearchBackendDep,
)
from .cache import ParameterizedCache
from .query import (
    AbstractGetQuery,
    AbstractSearchQuery,
    AbstractQueryFactory,
)
from ..cache import (
    AbstractCacheService,
    CacheServiceDep,
)


class AbstractSearchService(abc.ABC):
    @abc.abstractmethod
    async def get(self, *, query: AbstractGetQuery) -> dict | None: ...

    @abc.abstractmethod
    async def search(self, *, query: AbstractSearchQuery) -> list[dict] | None: ...

    @abc.abstractmethod
    def create_query(self) -> AbstractQueryFactory: ...


class SearchService(AbstractSearchService):
    search_backend: AbstractSearchBackend
    search_cache: ParameterizedCache

    def __init__(self,
                 *,
                 search_backend: AbstractSearchBackend,
                 cache_service: AbstractCacheService) -> None:
        self.search_backend = search_backend
        cache = cache_service.get_cache(key_prefix='search')
        self.search_cache = ParameterizedCache(cache=cache)

    async def get(self, *, query: AbstractGetQuery) -> dict | None:
        compiled_query = query.compile()
        result = await self.search_cache.get(params=compiled_query)

        if result is not None:
            return result

        result = await self.search_backend.get(query=compiled_query)

        if result is None:
            return None

        await self.search_cache.set(params=compiled_query, value=result)

        return result

    async def search(self, *, query: AbstractSearchQuery) -> list[dict] | None:
        compiled_query = query.compile()
        result = await self.search_cache.get(params=compiled_query)

        if result is not None:
            return result

        result = await self.search_backend.search(query=compiled_query)

        if result is None:
            return None

        await self.search_cache.set(params=compiled_query, value=result)

        return result

    def create_query(self) -> AbstractQueryFactory:
        return self.search_backend.create_query()


async def get_search_service(search_backend: SearchBackendDep,
                             cache_service: CacheServiceDep) -> AbstractSearchService:
    return SearchService(
        search_backend=search_backend,
        cache_service=cache_service,
    )


SearchServiceDep = Annotated[AbstractSearchService, Depends(get_search_service)]
