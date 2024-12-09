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
        genre: uuid.UUID = None,
        page_number: int = 1,
        page_size: int = 50,
        film_service: FilmService = Depends(get_film_service),
) -> list[Film]:

    sort_by = dict()
    if not sort:
        sort_by = {'field': 'id', 'order': SortOrderEnum.asc}
    else:
        if sort[0] == '-':
            sort_by['field'] = sort[1:]
            sort_by['order'] = SortOrderEnum.desc
        else:
            sort_by['field'] = sort
            sort_by['order'] = SortOrderEnum.asc

    film_list = await film_service.get_list(
        sort=sort_by,
        genre_uuid=genre,
        page_number=page_number,
        page_size=page_size
    )
    if not film_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return [Film(**item.model_dump()) for item in film_list]


# @todo use for test -> 5065b37b-fd5b-4c48-8a24-435198c44830
@router.get('/{id}', response_model=FilmInfo)
async def get_by_id(
        id: str,
        film_service: FilmService = Depends(get_film_service)
) -> FilmInfo:
    film = await film_service.get_by_id(id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return FilmInfo(**film.model_dump())


@router.get('/search/', response_model=list[Film])
async def search(
        query: str = '',
        page_number: int = 1,
        page_size: int = 50,
        film_service: FilmService = Depends(get_film_service),
) -> list[Film]:

    film_list = await film_service.search(query=query, page_number=page_number, page_size=page_size)
    if not film_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return [Film(**item.model_dump()) for item in film_list]
