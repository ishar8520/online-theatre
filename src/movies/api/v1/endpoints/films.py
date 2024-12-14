from __future__ import annotations

import uuid
from enum import Enum
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from movies.services.film import FilmService, get_film_service
from ..models.films import FilmInfo, Film

router = APIRouter()


class SortOrderEnum(str, Enum):
    asc = "asc"
    desc = "desc"


@router.get('/', response_model=list[Film])
async def get_list(
        sort: str = '',
        genre: uuid.UUID | None = None,
        page_number: int = 1,
        page_size: int = 50,
        film_service: FilmService = Depends(get_film_service),
) -> list[Film]:

    if page_size > 150:
        page_size = 50

    sort_by = {}
    if sort:
        is_first_dash = sort[0] == '-'

        field = sort[1:] if is_first_dash else sort
        sort = SortOrderEnum.desc if is_first_dash else SortOrderEnum.asc

        if field == 'imdb_rating':
            sort_by = {'field': 'rating', 'order': sort}

    if not sort_by:
        sort_by = {'field': 'id', 'order': SortOrderEnum.asc}

    film_list = await film_service.get_list(
        sort=sort_by,
        genre_uuid=genre,
        page_number=page_number,
        page_size=page_size
    )
    if not film_list:
        return []

    return [Film(**item.model_dump(by_alias=True)) for item in film_list]


@router.get('/{uuid}', response_model=FilmInfo)
async def get_by_id(
        uuid: uuid.UUID,
        film_service: FilmService = Depends(get_film_service)
) -> FilmInfo:
    film = await film_service.get_by_id(uuid)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Film not found')

    return FilmInfo(**film.model_dump(by_alias=True))


@router.get('/search/', response_model=list[Film])
async def search(
        query: str = '',
        page_number: int = 1,
        page_size: int = 50,
        film_service: FilmService = Depends(get_film_service),
) -> list[Film]:
    if not query:
        return []

    film_list = await film_service.search(query=query, page_number=page_number, page_size=page_size)
    if not film_list:
        return []

    return [Film(**item.model_dump(by_alias=True)) for item in film_list]
