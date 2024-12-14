from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from movies.services.genre import GenreService, get_genre_service
from ..models.genres import Genre

router = APIRouter()


@router.get('/', response_model=list[Genre])
async def get_list(
        page_number: int = 1,
        page_size: int = 50,
        get_genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre]:

    if page_size > 150:
        page_size = 50

    genre_list = await get_genre_service.get_list(
        page_number=page_number,
        page_size=page_size
    )
    if not genre_list:
        return []

    return [Genre(**item.model_dump(by_alias=True)) for item in genre_list]


@router.get('/{uuid}', response_model=Genre)
async def get_by_id(
        uuid: uuid.UUID,
        get_genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await get_genre_service.get_by_id(uuid)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genre not found')

    return Genre(**genre.model_dump(by_alias=True))
