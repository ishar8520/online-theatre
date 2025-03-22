from __future__ import annotations

import uuid

from pydantic import BaseModel

from ....service.models.base import NotificationType


class BaseMessageRequestDto(BaseModel):
    subject: str
    template_id: uuid.UUID
    notification_type: NotificationType = NotificationType.EMAIL


class BroadcastMessageRequestDto(BaseMessageRequestDto):
    pass


class PersonalizedMessageRequestDto(BaseMessageRequestDto):
    pass
