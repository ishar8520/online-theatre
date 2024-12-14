from __future__ import annotations

import uuid
from functools import lru_cache

from ..core import config
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from .abstract import AbstractService
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

        result = await self._search_in_elastic(index=config.ELASTIC_INDEX_NAME_PERSONS, body=body)

        if result is None:
            return list()

        return [Person(**item['_source']) for item in result]

    async def get_by_id(
            self,
            id: uuid.UUID
    ) -> Person | None:

        str_id = str(id)
        data = await self._get_from_cache(str_id)

        if not data:
            data = await self._get_from_elastic(index=config.ELASTIC_INDEX_NAME_PERSONS, id=str_id)
            if not data:
                return None

            person = Person(**data)
            await self._put_to_cache(str(person.id), person)

            return person

        return Person.model_validate_json(data)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
