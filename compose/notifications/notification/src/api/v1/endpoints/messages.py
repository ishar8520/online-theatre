from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from ....service.exceptions.queue import QueueSendException
from ....service.message import MessageServiceDep
from ..models.messages import (
    BroadcastMessageRequestDto,
    PersonalizedMessageRequestDto
)
from ....service.models.message import (
    PersonalizedMessageDto,
    BroadcastMessageDto
)

router = APIRouter()


@router.post(
    path='/broadcast',
    status_code=HTTPStatus.ACCEPTED,
    summary='Message broadcast',
    description='Send messages for all users'
)
async def send_for_all(
        broadcast_message: BroadcastMessageRequestDto,
        message_service: MessageServiceDep
) -> dict:

    message = BroadcastMessageDto(**broadcast_message.model_dump())

    try:
        result = await message_service.send_broadcast(message)
    except QueueSendException:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Internal error'
        )

    return {"result": result}


@router.post(
    path='/personalized/{user_id}',
    status_code=HTTPStatus.ACCEPTED,
    summary='Personalized message for user',
    description='Send personalized message for user'
)
async def send_for_user(
        user_id: uuid.UUID,
        personalized_message: PersonalizedMessageRequestDto,
        message_service: MessageServiceDep
) -> dict:

    message = PersonalizedMessageDto(user_id=user_id, **personalized_message.model_dump())

    try:
        result = await message_service.send_personalized(message)
    except QueueSendException:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Internal error'
        )

    return {"result": result}
