from __future__ import annotations

import uuid

from pydantic import BaseModel

from .base import NotificationType


class BaseMessageRequestDto(BaseModel):
    subject: str
    template_id: uuid.UUID | None = None
    text: str | None = None
    type: NotificationType = NotificationType.EMAIL


class BroadcastMessageRequestDto(BaseMessageRequestDto):
    pass


class PersonalizedMessageRequestDto(BaseMessageRequestDto):
    pass
