from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends

from .search import (
    SearchService,
    SearchServiceDep,
)
from ..core.config import settings
from ..models import Film


class FilmService:
    search_service: SearchService

    def __init__(self, *, search_service: SearchService) -> None:
        self.search_service = search_service

    async def get_list_by_person(
            self,
            person_uuid: uuid.UUID = None,
    ) -> list[Film]:

        body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {
                                    "term": {
                                        "actors.id": str(person_uuid)
                                    }
                                }
                            }
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {
                                    "term": {
                                        "directors.id": str(person_uuid)
                                    }
                                }
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {
                                    "term": {
                                        "writers.id": str(person_uuid)
                                    }
                                }
                            }
                        },
                    ],
                    "minimum_should_match": 1
                }
            }
        }

        result = await self.search_service.search(index=settings.elasticsearch.index_name_films, body=body)

        if result is None:
            return []

        return [Film(**source_item['_source']) for source_item in result]

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
                    "path": "genres",
                    "query": {
                        "term": {
                            "genres.id": str(genre_uuid)
                        }
                    }
                }
            }

        result = await self.search_service.search(index=settings.elasticsearch.index_name_films, body=body)

        if result is None:
            return []

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

        result = await self.search_service.search(index=settings.elasticsearch.index_name_films, body=body)

        if result is None:
            return []

        return [Film(**item['_source']) for item in result]

    async def get_by_id(
            self,
            id: uuid.UUID
    ) -> Film | None:
        data = await self.search_service.get(index=settings.elasticsearch.index_name_films, id=str(id))

        if not data:
            return None

        return Film(**data)


async def get_film_service(search_service: SearchServiceDep) -> FilmService:
    return FilmService(search_service=search_service)


FilmServiceDep = Annotated[FilmService, Depends(get_film_service)]
