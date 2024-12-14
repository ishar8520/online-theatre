from __future__ import annotations

from abc import ABC

from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from .search import SearchService


class AbstractService(ABC):
    search_service: SearchService

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch) -> None:
        self.search_service = SearchService(
            elasticsearch_client=elastic,
            redis_client=redis,
        )
