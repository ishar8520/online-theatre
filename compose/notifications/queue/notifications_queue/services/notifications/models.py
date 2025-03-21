from __future__ import annotations

import enum
import uuid

from pydantic import BaseModel


class NotificationType(enum.StrEnum):
    EMAIL = 'email'
    SMS = 'sms'
    PUSH = 'push'


class Notification(BaseModel):
    user_id: uuid.UUID | None = None
    subject: str | None = None
    text: str | None = None
    template_id: uuid.UUID | None = None
    template_context: dict | None = None
    type: NotificationType = NotificationType.EMAIL
