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
from ..models import Genre


class GenreService(AbstractService):

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


def get_genre_service(redis_client: RedisClientDep,
                      elasticsearch_client: ElasticsearchClientDep) -> GenreService:
    return GenreService(redis_client=redis_client, elasticsearch_client=elasticsearch_client)


GenreServiceDep = Annotated[GenreService, Depends(get_genre_service)]
