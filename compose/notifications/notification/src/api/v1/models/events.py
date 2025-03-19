from __future__ import annotations

import uuid

from pydantic import BaseModel


class EventRegistrationDto(BaseModel):
    user_id: uuid.UUID


class EventNewMovieDto(BaseModel):
    fim_id: uuid.UUID
