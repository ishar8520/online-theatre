from __future__ import annotations

import enum
import uuid

from pydantic import BaseModel


class NotificationType(enum.StrEnum):
    EMAIL = 'email'
    SMS = 'sms'
    PUSH = 'push'


class MessageBase(BaseModel):
    subject: str
    template_id: uuid.UUID
    text: str
    type: NotificationType = NotificationType.EMAIL


class MessageDto(MessageBase):
    user_id: uuid.UUID
