from __future__ import annotations

import uuid
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from .abstract import AbstractService
from ..core import config
from ..db import (
    get_elastic,
    get_redis,
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

        result = await self.search_service.search(index=config.ELASTIC_INDEX_NAME_GENRES, body=body)

        if result is None:
            return []

        return [Genre(**source_item['_source']) for source_item in result]

    async def get_by_id(
            self,
            id: uuid.UUID
    ) -> Genre | None:

        data = await self.search_service.get(index=config.ELASTIC_INDEX_NAME_GENRES, id=str(id))

        if not data:
            return None

        return Genre(**data)


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
