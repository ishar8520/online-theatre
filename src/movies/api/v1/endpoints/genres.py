from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from ..dependencies import PageDep
from ..models.genres import Genre
from ....services import GenreServiceDep

router = APIRouter()


@router.get(
    '/',
    response_model=list[Genre],
    summary='Get list of genres',
    description='Get list of genres with pagination. The maximum count of genres on one page are 150.'
)
async def get_list(*, page: PageDep, genre_service: GenreServiceDep) -> list[Genre]:
    genre_list = await genre_service.get_list(
        page_number=page.number,
        page_size=page.size
    )
    if not genre_list:
        return []

    return [Genre(**item.model_dump(by_alias=True)) for item in genre_list]


@router.get(
    '/{uuid}',
    response_model=Genre,
    summary='Get genre by uuid',
    description='Get concrete genre by uuid.'
)
async def get_by_id(*, uuid: uuid.UUID, genre_service: GenreServiceDep) -> Genre:
    genre = await genre_service.get_by_id(uuid)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genre not found')

    return Genre(**genre.model_dump(by_alias=True))
