from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BaseEvent(BaseModel):
    id: str
    user_id: UUID


class ClickEvent(BaseEvent):
    element: str
    timestamp: str


class PageViewEvent(BaseEvent):
    url: str
    duration: int
    timestamp: datetime


class CustomEvent(BaseEvent):
    event_type: str
    movie_quality: str = None
    movie_id: str = None
    filters: dict = None
    timestamp: datetime


class EventContainer:
    def __init__(self, model):
        self.model = model

    def model_dump_json(self):
        return self.model.model_dump_json()
