from __future__ import annotations

import abc
import dataclasses
import enum
import uuid

from pydantic import BaseModel


class NotificationType(enum.StrEnum):
    EMAIL = 'email'
    SMS = 'sms'
    PUSH = 'push'


class Notification(BaseModel, abc.ABC):
    type: NotificationType = NotificationType.EMAIL
    users: list[uuid.UUID] = []
    subject: str


class TextNotification(Notification):
    text: str


class TemplateNotification(Notification):
    template_id: uuid.UUID | None = None
    template_code: str | None = None
    template_context: dict = {}


@dataclasses.dataclass(kw_only=True)
class NotificationMessage:
    type: NotificationType = NotificationType.EMAIL
    subject: str
    text: str
