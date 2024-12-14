from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from movies.services.person import PersonService, get_person_service
from ..models.persons import Person, PersonFilm

router = APIRouter()


@router.get('/{uuid}', response_model=Person)
async def get_by_id(
        uuid: uuid.UUID,
        person_service: PersonService = Depends(get_person_service)
) -> Person:
    person = await person_service.get_by_id(uuid)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Person not found')

    return Person(**person.model_dump(by_alias=True))


@router.get('/{uuid}/film/', response_model=list[PersonFilm])
async def get_by_id_with_films(
        uuid: uuid.UUID,
        person_service: PersonService = Depends(get_person_service),
) -> list[PersonFilm]:

    person = await person_service.get_by_id(uuid)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Person not found')

    return [PersonFilm(**item.model_dump(by_alias=True)) for item in person]


@router.get('/search/', response_model=list[Person])
async def search(
        query: str = '',
        page_number: int = 1,
        page_size: int = 50,
        person_service: PersonService = Depends(get_person_service),
) -> list[Person]:

    if page_size > 150:
        page_size = 50

    person_list = await person_service.search(query=query, page_number=page_number, page_size=page_size)
    if not person_list:
        return []

    return [Person(**item.model_dump(by_alias=True)) for item in person_list]
