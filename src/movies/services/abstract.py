from abc import ABC

from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import BaseModel
from typing import Dict, List
from redis.asyncio import Redis

REDIS_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class AbstractService(ABC):

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def _get_from_elastic(self, index: str, id: str) -> Dict | None:
        try:
            doc = await self.elastic.get(index=index, id=id)
        except NotFoundError:
            return None

        return doc['_source']

    async def _search_in_elastic(self, index: str, body: Dict) -> List[Dict] | None:
        try:
            doc = await self.elastic.search(
                index=index,
                body=body
            )
        except NotFoundError:
            return None

        if not doc['hits']['hits']:
            return None

        return doc['hits']['hits']

    async def _get_from_cache(self, name: str) -> BaseModel | None:
        data = await self.redis.get(name)
        if not data:
            return None

        return data

    async def _put_to_cache(self, name: str, model: BaseModel):
        await self.redis.set(name, model.model_dump_json(), REDIS_CACHE_EXPIRE_IN_SECONDS)
