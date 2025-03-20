from http import HTTPStatus

from fastapi import APIRouter

from ....service.event import EventServiceDep
from ..models.events import (
    EventRegistrationDto,
    EventNewMovieDto
)

router = APIRouter()


@router.post(
    path='/registration',
    status_code=HTTPStatus.ACCEPTED,
    description='Send notification after user registration'
)
async def notify_on_registration(
    event: EventRegistrationDto,
    event_service: EventServiceDep
):
    return await event_service.on_user_registration(**event.model_dump())


@router.post(
    path='/new_movie',
    status_code=HTTPStatus.ACCEPTED,
    description='Send notification for all people who subscribe on new movies'
)
async def notify_on_new_movie(
    event: EventNewMovieDto,
    event_service: EventServiceDep
):
    result = await event_service.on_add_new_movie(**event.model_dump())

    return result
