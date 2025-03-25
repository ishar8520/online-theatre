from __future__ import annotations

from pydantic import BaseModel

from ....services.notifications import (
    TextNotification,
    TemplateNotification,
)


class SendNotificationResponse(BaseModel):
    task_id: str


class TextNotificationsBulk(BaseModel):
    notifications: list[TextNotification] = []


class TemplateNotificationsBulk(BaseModel):
    notifications: list[TemplateNotification] = []
