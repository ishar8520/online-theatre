from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends

from .search import (
    SearchService,
    SearchServiceDep,
)
from ..core.config import settings
from ..models import Person


class PersonService:
    search_service: SearchService

    def __init__(self, *, search_service: SearchService) -> None:
        self.search_service = search_service

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


async def get_person_service(search_service: SearchServiceDep) -> PersonService:
    return PersonService(search_service=search_service)


PersonServiceDep = Annotated[PersonService, Depends(get_person_service)]
