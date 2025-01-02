from __future__ import annotations

from abc import ABC

import elasticsearch
import redis.asyncio as redis

from .search import SearchService


class AbstractService(ABC):
    search_service: SearchService

    def __init__(self,
                 *,
                 redis_client: redis.Redis,
                 elasticsearch_client: elasticsearch.AsyncElasticsearch) -> None:
        self.search_service = SearchService(
            elasticsearch_client=elasticsearch_client,
            redis_client=redis_client,
        )
