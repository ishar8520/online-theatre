from __future__ import annotations

import uuid

from pydantic import BaseModel


class ReviewAdd(BaseModel):
    user_id: uuid.UUID
    film_id: uuid.UUID
    text: str
    is_published: bool = False


class ReviewUpdate(BaseModel):
    text: str
