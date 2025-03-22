from __future__ import annotations

import uuid

from pydantic import BaseModel

from ....service.models.base import NotificationType


class EventRegistrationRequestDto(BaseModel):
    user_id: uuid.UUID
    notification_type: NotificationType = NotificationType.EMAIL


class EventNewMovieRequestDto(BaseModel):
    film_id: uuid.UUID
    notification_type: NotificationType = NotificationType.EMAIL
