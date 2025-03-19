from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import APIRouter

from ..models.messages import (
    MessageBroadcastDto,
    MessagePersonalizedDto
)

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
        message: MessagePersonalizedDto
) -> dict:
    return message.model_dump()
