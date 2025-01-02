from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends

from .search import (
    SearchService,
    SearchServiceDep,
)
from ..core.config import settings
from ..models import Genre


class GenreService:
    search_service: SearchService

    def __init__(self, *, search_service: SearchService) -> None:
        self.search_service = search_service

    async def get_list(
            self,
            page_number: int,
            page_size: int,
    ) -> list[Genre]:

        body = {
            "size": page_size,
            "from": (page_number - 1) * page_size,
        }

        result = await self.search_service.search(index=settings.elasticsearch.index_name_genres, body=body)

        if result is None:
            return []

        return [Genre(**source_item['_source']) for source_item in result]

    async def get_by_id(
            self,
            id: uuid.UUID
    ) -> Genre | None:

        data = await self.search_service.get(index=settings.elasticsearch.index_name_genres, id=str(id))

        if not data:
            return None

        return Genre(**data)


async def get_genre_service(search_service: SearchServiceDep) -> GenreService:
    return GenreService(search_service=search_service)


GenreServiceDep = Annotated[GenreService, Depends(get_genre_service)]
