from __future__ import annotations

import uuid
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from .abstract import AbstractService
from ..core.config import settings
from ..db import (
    get_elastic,
    get_redis,
)
from ..models import Person


class PersonService(AbstractService):

    async def search(
            self,
            query: str,
            page_number: int,
            page_size: int
    ) -> list[Person] | None:

        body = {
            "query": {
                "match": {
                    "full_name": query
                }
            },
            "size": page_size,
            "from": (page_number - 1) * page_size,
        }

        result = await self.search_service.search(index=settings.elasticsearch.index_name_persons, body=body)

        if result is None:
            return []

        return [Person(**item['_source']) for item in result]

    async def get_by_id(
            self,
            id: uuid.UUID
    ) -> Person | None:
        data = await self.search_service.get(index=settings.elasticsearch.index_name_persons, id=str(id))

        if not data:
            return None

        return Person(**data)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
