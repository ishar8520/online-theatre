from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import APIRouter

from ....service.message import MessageServiceDep
from ..models.messages import (
    MessageBroadcastDto,
    MessagePersonalizedDto
)
from ....service.models.message import MessageDto

router = APIRouter()


@router.post(
    path='/broadcast',
    status_code=HTTPStatus.ACCEPTED,
    description='Send messages for all users'
)
async def broadcast(message: MessageBroadcastDto) -> dict:

    return message.model_dump()


@router.post(
    path='/personalized/{user_id}',
    status_code=HTTPStatus.ACCEPTED,
    description='Send personalized message for user'
)
async def send_for_user(
        user_id: uuid.UUID,
        personalized_message: MessagePersonalizedDto,
        message_service: MessageServiceDep
) -> dict:

    message = MessageDto(user_id=user_id, **personalized_message.model_dump())

    return await message_service.send_personalized(message)
