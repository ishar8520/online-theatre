from __future__ import annotations

import uuid

from pydantic import BaseModel

from .base import NotificationType


class EventRegistrationDto(BaseModel):
    user_id: uuid.UUID
    type: NotificationType = NotificationType.EMAIL


class EventNewMovieDto(BaseModel):
    film_id: uuid.UUID
    type: NotificationType = NotificationType.EMAIL
