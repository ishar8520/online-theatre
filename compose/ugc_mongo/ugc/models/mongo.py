from __future__ import annotations

import uuid
from datetime import datetime, timezone

from beanie import Document
from pydantic import Field


class Bookmark(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    film_id: uuid.UUID
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        collection = "bookmarks"
