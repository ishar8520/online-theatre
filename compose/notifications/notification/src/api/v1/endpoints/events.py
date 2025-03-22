from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from ....service.event import EventServiceDep
from ..models.events import (
    EventRegistrationRequestDto,
    EventNewMovieRequestDto
)
from ....service.exceptions.queue import QueueSendException

router = APIRouter()


@router.post(
    path='/registration',
    status_code=HTTPStatus.ACCEPTED,
    summary='On new user',
    description='Send notification after user registration'
)
async def notify_on_registration(
    event: EventRegistrationRequestDto,
    event_service: EventServiceDep
):
    try:
        result =  await event_service.on_user_registration(**event.model_dump())
    except QueueSendException:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Internal error'
        )

    return {"result": result}


@router.post(
    path='/new_movie',
    status_code=HTTPStatus.ACCEPTED,
    summary='On new movie',
    description='Send notification for all people who subscribe on new movies'
)
async def notify_on_new_movie(
    event: EventNewMovieRequestDto,
    event_service: EventServiceDep
) -> dict:
    try:
        result = await event_service.on_add_new_movie(**event.model_dump())
    except QueueSendException:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Internal error'
        )

    return {"result": result}
