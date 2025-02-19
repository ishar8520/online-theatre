from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BaseEvent(BaseModel):
    type: str
    timestamp: datetime
    user_id: UUID | None = None
    fingerprint: str
    element: list[str]
    url: str


class EventContainer(BaseModel):
    event: BaseEvent
