from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends

from .abstract import AbstractService
from ..core.config import settings
from ..db import (
    ElasticsearchClientDep,
    RedisClientDep,
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


def get_person_service(redis_client: RedisClientDep,
                       elasticsearch_client: ElasticsearchClientDep) -> PersonService:
    return PersonService(redis_client=redis_client, elasticsearch_client=elasticsearch_client)


PersonServiceDep = Annotated[PersonService, Depends(get_person_service)]
