from __future__ import annotations

import uuid
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from .abstract import AbstractService
from ..db import (
    get_elastic,
    get_redis,
)
from ..models import Film

FILM_ELASTIC_INDEX_NAME = 'movies'


class FilmService(AbstractService):

    async def get_list(
            self,
            sort: dict[str, str],
            page_number: int,
            page_size: int,
            genre_uuid: uuid.UUID = None,
    ) -> list[Film]:

        body = {
            "sort": {
                sort['field']: {
                    "order": sort['order']
                }
            },
            "size": page_size,
            "from": (page_number - 1) * page_size,
        }

        if genre_uuid:
            body["query"] = {
                "nested": {
                    # @todo only for test
                    # "path": "genres",
                    "path": "actors",
                    "query": {
                        "term": {
                            # @todo only for test
                            # "genres.id": genre_uuid
                            "actors.id": genre_uuid
                        }
                    }
                }
            }

        result = await self._search_in_elastic(index=FILM_ELASTIC_INDEX_NAME, body=body)

        if result is None:
            return list()

        return [Film(**source_item['_source']) for source_item in result]

    async def search(
            self,
            query: str,
            page_number: int,
            page_size: int
    ) -> list[Film] | None:

        body = {
            "query": {
                "match": {
                    "title": query
                }
            },
            "size": page_size,
            "from": (page_number - 1) * page_size,
        }

        result = await self._search_in_elastic(index=FILM_ELASTIC_INDEX_NAME, body=body)

        if result is None:
            return list()

        return [Film(**item['_source']) for item in result]

    async def get_by_id(
            self,
            id: str
    ) -> Film | None:

        data = await self._get_from_cache(id)

        if not data:
            data = await self._get_from_elastic(FILM_ELASTIC_INDEX_NAME, id)
            if not data:
                return None

            film = Film(**data)
            await self._put_to_cache(film.id, film)

            return film

        return Film.model_validate_json(data)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
