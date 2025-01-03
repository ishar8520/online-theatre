from __future__ import annotations

import abc
from typing import Annotated

import backoff
import elasticsearch
from fastapi import Depends

from .query import (
    AbstractCompiledGetQuery,
    CompiledElasticsearchGetQuery,
    AbstractCompiledSearchQuery,
    CompiledElasticsearchSearchQuery,
    AbstractQueryFactory,
    ElasticsearchQueryFactory,
)
from ...db import ElasticsearchClientDep


class AbstractSearchBackend(abc.ABC):
    @abc.abstractmethod
    async def get(self, *, query: AbstractCompiledGetQuery) -> dict | None: ...

    @abc.abstractmethod
    async def search(self, *, query: AbstractCompiledSearchQuery) -> list[dict] | None: ...

    @abc.abstractmethod
    def create_query(self) -> AbstractQueryFactory: ...


class ElasticsearchSearchBackend(AbstractSearchBackend):
    elasticsearch_client: elasticsearch.AsyncElasticsearch
    query_factory: ElasticsearchQueryFactory

    def __init__(self, *, elasticsearch_client: elasticsearch.AsyncElasticsearch) -> None:
        self.elasticsearch_client = elasticsearch_client
        self.query_factory = ElasticsearchQueryFactory()

    @backoff.on_exception(backoff.expo, (
            elasticsearch.exceptions.ConnectionError,
            elasticsearch.exceptions.ConnectionTimeout,
    ))
    async def get(self, *, query: CompiledElasticsearchGetQuery) -> dict | None:
        try:
            response = await self.elasticsearch_client.get(index=query.index, id=query.id)
        except elasticsearch.NotFoundError:
            return None

        return response['_source']

    @backoff.on_exception(backoff.expo, (
            elasticsearch.exceptions.ConnectionError,
            elasticsearch.exceptions.ConnectionTimeout,
    ))
    async def search(self, *, query: CompiledElasticsearchSearchQuery) -> list[dict] | None:
        try:
            response = await self.elasticsearch_client.search(index=query.index, body=query.body)
        except elasticsearch.NotFoundError:
            return None

        results = response['hits']['hits']

        if not results:
            return None

        return [result['_source'] for result in results]

    def create_query(self) -> ElasticsearchQueryFactory:
        return self.query_factory


async def get_search_backend(elasticsearch_client: ElasticsearchClientDep) -> AbstractSearchBackend:
    return ElasticsearchSearchBackend(elasticsearch_client=elasticsearch_client)


SearchBackendDep = Annotated[AbstractSearchBackend, Depends(get_search_backend)]
