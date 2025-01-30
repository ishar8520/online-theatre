from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from ..dependencies import PageDep
from ..models.persons import Person, PersonFilm
from ....services import (
    PersonServiceDep,
    FilmServiceDep,
)
from ....services.auth.user import AuthUserDep

router = APIRouter()


@router.get(
    '/{uuid}',
    response_model=Person,
    summary='Get person by uuid',
    description='Get concrete person by uuid with list of films and roles.',
)
async def get_by_id(
        *,
        uuid: uuid.UUID,
        person_service: PersonServiceDep,
        auth_user: AuthUserDep
) -> Person:
    person = await person_service.get_by_id(uuid)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Person not found')

    return Person(**person.model_dump(by_alias=True))


@router.get(
    '/{uuid}/film/',
    response_model=list[PersonFilm],
    summary='Get list of films by person uuid',
    description='Get list of films with imdb rating by person uuid.'
)
async def get_by_id_with_films(
        *,
        uuid: uuid.UUID,
        film_service: FilmServiceDep,
        auth_user: AuthUserDep
) -> list[PersonFilm]:
    films_person = await film_service.get_list_by_person(uuid)
    if not films_person:
        return []

    return [PersonFilm(**item.model_dump(by_alias=True)) for item in films_person]


@router.get(
    '/search/',
    response_model=list[Person],
    summary='Search persons',
    description='Search persons with list of films and roles by their full name with pagination. The maximum count of items on one page are 150.'
)
async def search(
        *,
        query: str = '',
        page: PageDep,
        person_service: PersonServiceDep,
        auth_user: AuthUserDep
) -> list[Person]:
    person_list = await person_service.search(query=query, page_number=page.number, page_size=page.size)
    if not person_list:
        return []

    return [Person(**item.model_dump(by_alias=True)) for item in person_list]
