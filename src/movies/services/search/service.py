from __future__ import annotations

import abc
from typing import Annotated

from fastapi import Depends

from .backends import (
    AbstractSearchBackend,
    SearchBackendDep,
    AbstractQuery,
    AbstractGetQuery,
    AbstractSearchQuery,
    AbstractQueryFactory,
)
from ..cache import (
    AbstractCacheService,
    CacheServiceDep,
    ParameterizedCache,
)


class AbstractSearchService(abc.ABC):
    @abc.abstractmethod
    async def get(self, *, query: AbstractGetQuery) -> dict | None: ...

    @abc.abstractmethod
    async def search(self, *, query: AbstractSearchQuery) -> list[dict] | None: ...

    @abc.abstractmethod
    def create_query(self) -> AbstractQueryFactory: ...


class SearchService(AbstractSearchService):
    backend: AbstractSearchBackend
    cache: ParameterizedCache

    def __init__(self, *, backend: AbstractSearchBackend, cache_service: AbstractCacheService) -> None:
        self.backend = backend
        cache = cache_service.get_cache(key_prefix='search')
        self.cache = ParameterizedCache(cache=cache)

    async def get(self, *, query: AbstractGetQuery) -> dict | None:
        return await self._execute_query(query=query)

    async def search(self, *, query: AbstractSearchQuery) -> list[dict] | None:
        return await self._execute_query(query=query)

    async def _execute_query[TResult](self, *, query: AbstractQuery[TResult]) -> TResult:
        compiled_query = query.compile()
        result = await self.cache.get(params=compiled_query)

        if result is not None:
            return result

        result = await compiled_query.execute(backend=self.backend)

        if result is None:
            return None

        await self.cache.set(params=compiled_query, value=result)

        return result

    def create_query(self) -> AbstractQueryFactory:
        return self.backend.create_query()


async def get_search_service(backend: SearchBackendDep, cache_service: CacheServiceDep) -> AbstractSearchService:
    return SearchService(backend=backend, cache_service=cache_service)


SearchServiceDep = Annotated[AbstractSearchService, Depends(get_search_service)]
