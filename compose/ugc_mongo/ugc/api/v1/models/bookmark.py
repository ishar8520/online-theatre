from __future__ import annotations

import uuid

from pydantic import BaseModel


class BookmarkAdd(BaseModel):
    user_id: uuid.UUID
    film_id: uuid.UUID

class BookmarkDelete(BaseModel):
    uuid: uuid.UUID
